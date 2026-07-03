from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.llms.groqllm import GroqModel, AudioToTextGroqModel
from src.states.blogstate import BlogState
from src.states.transcriptstate import VideoAgentState
from src.nodes.blognode import BlogNode
from src.nodes.transcriptnode import TranscriptNode


class GraphBuilder:
    def __init__(self, model, audio_model):
        self.model = model
        self.audio_model = audio_model
    
    def build_graph(self):
        """
        Build Graph for generating Blog from Topic using LLM
        """
        self.graph = StateGraph(BlogState)
        self.blog_node = BlogNode(self.model)
        self.graph.add_node("title_creator",self.blog_node.title_creation)
        self.graph.add_node("content_generator",self.blog_node.content_generation)
        
        self.graph.add_edge(START, "title_creator")
        self.graph.add_conditional_edges(
            "title_creator",
            self.blog_node.ErrorHandlerEdge,
            {
                "carryon":"content_generator",
                "__end__":END
            }
        )
        self.graph.add_edge("title_creator", "content_generator")
        self.graph.add_edge("content_generator", END)

        return self.graph
    
    def build_transcript_graph(self):
        """
        Build Graph for generating Transcript from Video using LLM
        """
        self.graph = StateGraph(VideoAgentState)
        self.transcript_node = TranscriptNode(self.audio_model, self.model)
        self.graph.add_node("userinputnode",self.transcript_node.UserInputNode)
        self.graph.add_node("videodatainputnode",self.transcript_node.VideoDataFetcherNode)
        self.graph.add_node("video_transcriber",self.transcript_node.TranscriptingNode)
        self.graph.add_node("articlewriter",self.transcript_node.ArticleWriterNode)
        self.graph.add_node("review",self.transcript_node.ArticleReviewerNode)
        self.graph.add_node("translate", self.transcript_node.TranslatorNode)

        self.graph.add_conditional_edges(
            START,
            self.transcript_node.ErrorHandlerEdge,
            {
                "carryon":"userinputnode",
                "__end__":END
            },
        )
        self.graph.add_conditional_edges(
            "userinputnode",
            self.transcript_node.ErrorHandlerEdge,
            {
                "carryon":"videodatainputnode",
                "__end__":END
            },
        )
        self.graph.add_conditional_edges(
            "videodatainputnode",
            self.transcript_node.ErrorHandlerEdge,
            {
                "carryon":"video_transcriber",
                "__end__":END
            },
        )
        self.graph.add_conditional_edges(
            "video_transcriber",
            self.transcript_node.ErrorHandlerEdge,
            {
                "carryon":"articlewriter",
                "__end__":END
            },
        )
        self.graph.add_conditional_edges(
            "articlewriter",
            self.transcript_node.ErrorHandlerEdge,
            {
                "carryon":"review",
                "__end__":END
            },
        )
        self.graph.add_conditional_edges(
            "review",
            self.transcript_node.ReviewConditionEdge,
            {"translate": "translate", "regenerate": "articlewriter", "__end__": END}
        )
        self.graph.add_edge("translate", END)

        return self.graph
    
    def setup_graph(self, usecase):
        if usecase == "blog":
            return self.build_graph().compile(checkpointer=MemorySaver())
        elif usecase == "transcript":
            return self.build_transcript_graph().compile(checkpointer=MemorySaver())
        else:
            raise ValueError("Usecase not found")
        
    def delete_memory(self, graph, config):
        graph.update_state(config, values=None)

# ## below code is for langsmith - langgraph studio
# chat_model = GroqModel().get_model()
# audio_model = AudioToTextGroqModel().get_model()
# # graph = GraphBuilder(chat_model, audio_model).build_graph().compile()
# graph = GraphBuilder(chat_model, audio_model).build_transcript_graph().compile()