from typing import List, Optional, Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class CodeChange(BaseModel):
    """Changes to make to the file."""

    change_type: Literal["delete", "modify", "add_after"] = Field(description="The type of change to make.")
    line_start: int = Field(description="The starting line of the change. Please verify that the line number is correct.")
    line_end: int = Field(description="The end line of the change. Please verify that the line number is correct.")
    content: str = Field(description="The code changes to make to these lines")

class ChangedCode(BaseModel):
    """The code snippet with the patch applied."""

    content: str = Field(description="code snippet with the code applied.")

class Patch(BaseModel):
    start: Optional[int] = Field(description="start line of the patch")
    end: Optional[int] = Field(description="end line of the patch")
    code_snippet: Optional[str] = Field(description="original piece of code to apply patch to")
    patch: Optional[str] = Field(description="code snippet after applying the patch")

class FileChange(BaseModel):
    """List of all the changes to make to the file."""
    changes: list[CodeChange] = Field(description="List of specific code changes")
    title: str = Field(description="Overall title for the change mande. This will go into the pull request title.")
    description: str = Field(description="High-level description for all the changes made. This will be the description of the pull request.")

class ApprovalResult(BaseModel):
    """Approval Results for making the change."""
    is_approved: bool = Field(description="Boolean for whether or not to approve the change.")
    approval_message: str = Field(description="High level comments about the latency improvements.")

class CodeChangeGenerator:
    def __init__(self):
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        structured_llm = llm.with_structured_output(FileChange)
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", get_system_message()),
            ("user", get_prompt())
        ])


        self.runnable = prompt_template | structured_llm

    def get_response(self, file: dict, latency_results: dict) -> FileChange:
        res = self.runnable.invoke(
            {
                "file_name": file['filename'], 
                "file_content": file['content'], 
                "patch": file['patch'],
                "latency_results": latency_results
            })
        
        return res 

def get_prompt():
    return """
    Given the following information about a file that has been changed and its latency profile, what optimizations would you suggest to reduce latency? Only suggest changes when you're confident they will improve the latency, as the results will be evaluated by a profiler.

    File path: {file_name}
    
    File content: {file_content}
    
    File changes: {patch}

    Latency profile results: {latency_results}"

    Please provide specific optimization suggestions based on this information. Return the file updated with the changes made.
    """

def get_system_message():
    return """You are an AI assistant and a smart software engineer. You are specialized in improving code performance and runtime."""

class LineChangeFixer:
    def __init__(self):
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        structured_llm = llm.with_structured_output(ChangedCode)
        system = """
        You are a smart and cautious software engineer
        """
        prompt = """
        Given the following snippet of code, apply the following patches to it.

        Code Snippet:
        {code_snippet}
        
        Patches: 
        {patch}
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", prompt)
        ])


        self.runnable = prompt_template | structured_llm

    def get_response(self, file: dict, code_change_list: List[CodeChange]) -> Patch:
        if not code_change_list:
            return Patch(patch=None)
        st = min([i.line_start for i in code_change_list])
        end = max([i.line_end for i in code_change_list])
        adjusted_st = max(0, st - 10)
        adjusted_end = end + 10
        # split file content by lines 
        code_snippet = '\n'.join(file['content'].split('\n')[adjusted_st:adjusted_end])
        res = self.runnable.invoke(
            {
                "code_snippet": code_snippet, 
                "patch": [i.model_dump() for i in code_change_list]
            })

        
        return Patch(start=adjusted_st, end=adjusted_end, code_snippet=code_snippet, patch=res.content)

class ChangeApprover:
    def __init__(self):
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        structured_llm = llm.with_structured_output(ApprovalResult)
        system = """
        You are a smart and cautious software engineer
        """
        prompt = """
        You are provided with three latency profile results for the same code.

        Results 1: 
        {before_results}

        Results 2 (with some latency optimizations):
        {after_results}

        Based on the following results, do you suggest we approve the change? A change should only be approved if it is better. It doesn't have to be significantly better, but just marginally better. In addition, provide a very high-level message about the improvements you noticed. For example, say something like 'The proposed optimization improved the overall latency by 23%, and specifically the function foo that improved by 50%.'
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", prompt)
        ])


        self.runnable = prompt_template | structured_llm

    def get_response(self, before_results, after_results) -> ApprovalResult:
        res = self.runnable.invoke(
            {
                "before_results": before_results, 
                "after_results": after_results
            })

        
        return res