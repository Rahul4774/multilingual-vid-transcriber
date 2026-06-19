from src.states.blogstate import BlogState
from src.states.errorstate import ErrorState
import traceback

class BlogNode:
    """
    Class to represent blog nodes, which will be used in the graph
    """
    def __init__(self, model):
        self.model = model
    
    def title_creation(self, state:BlogState):
        """
        Blog Title Creation Node
        """
        try:
            topic = state.get("topic", None)
            if not topic is None and topic.strip() != "":
                prompt = """
                    You are an expert blog title writer. use markdown formating.
                    generate a single blog title for the given topic. the title should be creative and SEO friendly.
                    topic : {topic}
                """
                system_prompt = prompt.format(topic=topic)
                response = self.model.invoke(system_prompt)
                state["blog"] = {"title":response.content}
            else:
                state["error"] = ErrorState(error="Please provide topic",status=400,message="Topic is required for title creation")
            return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to topic from user input: {e}",status=500,message="User input failed")
            return state

    def content_generation(self,state:BlogState):
        """
        Blog Content Generation Node
        """
        try:
            topic = state.get("topic", None)
            blog = state.get("blog", None)
            if not topic is None and topic.strip() != "":
                prompt = """
                    You are an expert blog content writer. use markdown formating.
                    generate a detailed blog content for the given topic. the content should be creative and SEO friendly.
                    topic : {topic}
                """
                system_prompt = prompt.format(topic=topic)
                response = self.model.invoke(system_prompt)
                state["blog"] = {"title":blog.get("title"), "content":response.content}
                return state
            else:
                state["error"] = ErrorState(error="Please provide topic",status=400,message="Topic is required for content generation")
                return state
        except Exception as e:
            # print(traceback.print_exc())
            state["error"] = ErrorState(error=f"Failed to generate content: {e}",status=500,message="Content generation failed")
            return state
    
    def ErrorHandlerEdge(self,state:BlogState):
        try:
            if state.get("error") is not None:
                return "__end__"
            else:
                return "carryon"
        except Exception as e:
            print(traceback.print_exc())
            return "__end__"