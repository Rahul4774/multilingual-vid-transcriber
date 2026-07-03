from langchain_core.outputs import chat_result
import os, traceback, requests
import ffmpeg
import yt_dlp
from src.states.transcriptstate import VideoAgentState, VideoState, Articlereview, UserInput
from src.states.errorstate import ErrorState

class TranscriptNode:
    def __init__(self,model,chat_model):
        self.model = model
        self.chatmodel = chat_model
        self.inputModel = chat_model.with_structured_output(UserInput)
        self.reviewmodel = chat_model.with_structured_output(Articlereview)

    def UserInputNode(self,state:VideoAgentState):
        try:
            print('user input node entry')
            if state.get("error", None) is not None:
                return state
            if not state.get("videoinput") or state.get("videoinput") == "":
                state["error"] = ErrorState(error="Please provide the video input",status=400,message="Video input is required")
                return state
            user_input = state.get("videoinput")
            prompt = """
            You are an information extraction assistant.
            Your task is to extract the video URL and language from the user's input.
            Rules:
            1. Find the video URL provided by the user.
            2. Find the language requested by the user for transcription/processing. if not then default to english.
            3. Return only valid JSON.
            4. Do not add any explanation or extra text.
            5. If a url field is not found, return None.
            Now extract from this user input:
            {user_input}"""
            system_prompt = prompt.format(user_input = state.get("videoinput"))
            response = self.inputModel.invoke(system_prompt)
            if response.url is None:
                state["error"] = ErrorState(error="Please provide the URL for the video",status=400,message="Video URL is required")
                return state
            state["videopath"] = response.url
            state["language"] = response.language
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to get user input: {e}",status=500,message="User input failed")
            return state
        finally:
            print('user input node exit')
        
    def VideoDataFetcherNode(self, state: VideoAgentState):
        try:
            if not state.get("videopath") or state.get("videopath") == "":
                state["error"] = ErrorState(error="Please provide the URL for the video",status=400,message="Video URL is required")
                return state
            url = state.get("videopath")
            video_state = None
            # Download video data into memory
            ydl_opts = {
                # "format": "bestaudio/best",
                "format": "best[height<=480]/bestvideo[height<=480]+bestaudio",
                "quiet": True,
                "noplaylist": True
                }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_state = VideoState(videotitle=info["title"])
                state["summary"] = info["title"]
                # if info["_type"] == "playlist":
                #     raise ValueError("This seems playlist it will cost you more please provide single video url")
                audio_url = info["url"]
            process = (
                ffmpeg
                .input(audio_url)
                .output(
                    "pipe:1",
                    format="mp3",
                    acodec="libmp3lame",
                    audio_bitrate="192k"
                )
                .run_async(
                    pipe_stdin=True,
                    pipe_stdout=True,
                    pipe_stderr=True
                )
            )
            audio_bytes, error = process.communicate()
            if process.returncode != 0:
                state["error"] = ErrorState(error="Failed to convert to audio",status=400,message=error)
                return state
            if not video_state:
                video_state = VideoState(audiodata=audio_bytes)
            else:
                video_state.audiodata = audio_bytes
            state["video_data"] = video_state
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to fetch video data: {e}",status=500,message="Video data fetch failed")
            return state
    
    def TranscriptingNode(self, state:VideoAgentState):
        try:
            video_data = state.get("video_data")
            if not video_data or video_data.audiodata == None:
                state["error"] = ErrorState(error="Please provide the audio data for the transcript",status=400,message="Audio data is required")
                return state
            with open("audio.mp3", "wb") as f:
                f.write(video_data.audiodata)
            with open("audio.mp3", "rb") as audio_data:
                result = self.model.audio.transcriptions.create(
                    file=audio_data,
                    model="whisper-large-v3",
                    language="en"
                )
            state["transcript"] = result.text
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to generate transcript: {e}",status=500,message="Transcript generation failed")
            return state
        
    def ArticleWriterNode(self, state:VideoAgentState):
        try:
            transcript = state.get("transcript")
            summary = state.get("summary")
            video_data = state.get("video_data")
            if not video_data:
                state["error"] = ErrorState(error="Please provide the video data for the article",status=400,message="Video data is required")
                return state
            videotitle = video_data.videotitle
            if not transcript or transcript == "":
                state["error"] = ErrorState(error="Please provide the transcript for the article",status=400,message="Transcript is required")
                return state
            if not summary or summary == "":
                state["error"] = ErrorState(error="Please provide the summary for the article",status=400,message="Summary is required")
                return state
            if not videotitle or videotitle == "":
                state["error"] = ErrorState(error="Please provide the title for the article",status=400,message="Video title is required")
                return state
            prompt = """
                You are an expert SEO content writer. Transform this video transcript and summary into a high-quality, publish-ready blog article.
                --- Inputs ---
                Title: {videotitle}
                Description: {summary}
                Transcript: {transcript}

                --- Rules ---
                1. Title: Use {videotitle} as the main article header.
                2. Format: Max 3 paragraphs per section. Use bullet/numbered lists for steps.
                3. Content: Write a comprehensive deep-dive. Include all transcript insights, steps, and data.
                4. Structure: Include a compelling Intro hook, themed body sections, a key-takeaway Conclusion, and a reader-engaging CTA.

                Draft the complete article now:"""
            systm_prompt = prompt.format(videotitle=videotitle,summary=summary,transcript=transcript)
            response = self.chatmodel.invoke(systm_prompt)
            state["finalarticle"] = response.content
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to generate article: {e}",status=500,message="Article generation failed")
            return state
    
    def ArticleReviewerNode(self,state:VideoAgentState):
        try:
            transcript = state.get("transcript")
            if not transcript or transcript == "":
                state["error"] = ErrorState(error="Please provide the transcript for the article",status=400,message="Transcript is required")
                return state
            summary = state.get("summary")
            if not summary or summary == "":
                state["error"] = ErrorState(error="Please provide the summary for the article",status=400,message="Summary is required")
                return state
            finalarticle = state.get("finalarticle")
            if not finalarticle or finalarticle == "":
                raise ValueError("Please provide the final article for review")
            prompt = """You are an expert content reviewer. Your task is to evaluate the provided Article against its source Context (video transcript and description) for publishing readiness, relevance, and compliance.
                --- Inputs ---
                Context (Source Material):
                Video Transcript: {transcript}
                Video Description: {summary}

                Article to Review:
                {finalarticle}

                --- Evaluation Rubric ---
                1. RELEVANCE (0.0 - 100.0):
                - Measure how accurately the Article reflects the core facts, themes, and details in the Context.
                - Deduct points if the Article hallucination details, introduces unrelated topics, or misses the core message of the video.

                2. COMPLIANCE (0.0 - 100.0):
                - Measure how well the Article adheres to professional publishing standards: flawless grammar, clear readability, logical structural flow, and basic SEO optimization (use of headers, concise paragraphs).
                - Deduct points for grammatical errors, poor formatting, or awkward phrasing.

                --- Rules ---
                1. Analyze the text rigorously based on the rubric above.
                2. Determine if modifications are required (`needchanges`: "yes" or "no") before this can be published. If either Relevance or Compliance is below 90.0, `needchanges` must be "yes".
                3. Draft clear, actionable, bulleted suggestions highlighting exactly what to fix or improve.

                Generate your review strictly matching the required Articlereview JSON schema:"""
            systm_prompt = prompt.format(finalarticle=finalarticle,transcript=transcript,summary=summary)
            response = self.reviewmodel.invoke(systm_prompt)
            state["review"] = response
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to review article: {e}",status=500,message="Review failed")
            return state

    def TranslatorNode(self, state:VideoAgentState):
        try:
            finalarticle = state.get("finalarticle")
            if not finalarticle or finalarticle == "":
                state["error"] = ErrorState(error="Please provide the final article for review",status=400,message="Final article is required")
                return state
            language = state.get("language")
            if not language or language == "":
                state["error"] = ErrorState(error="Please provide the language for the article",status=400,message="Language is required")
                return state
            prompt = """
                You are an expert Translator. Translate this content into the given language.
                --- Inputs ---
                content: {finalarticle}
                language: {language}

                --- Rules ---
                1. Format: Use Markdown
                2. Style: Write in {language}. Convert spoken filler/ticks into authoritative, professional, and accessible prose.
                3. Structure: Include a compelling Intro hook, themed body sections, a key-takeaway Conclusion, and a reader-engaging CTA."""
            systm_prompt = prompt.format(finalarticle=finalarticle,language=language)
            response = self.chatmodel.invoke(systm_prompt)
            state["video_data"] = None
            state["finalarticle"] = response.content
            return state
           
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to translate article: {e}",status=500,message="Translation failed")
            return state
    
    def ReviewConditionEdge(self,state:VideoAgentState):
        try:
            if state.get("error", None) is not None:
                return "__end__"
            review = state.get("review")
            if not review or review == "":
                return "review"
            if review.needchanges == "yes":
                if review.relevance_percentage < 65:
                    return "articlewriter"
            return "translate"
        except Exception as e:
            print(traceback.print_exc())
            return "__end__"
    
    def ErrorHandlerEdge(self, state:VideoAgentState):
        try:
            if state.get("error") is not None:
                return "__end__"
            else:
                return "carryon"
        except Exception as e:
            print(traceback.print_exc())
            return "__end__"