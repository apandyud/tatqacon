#curl -X POST http://172.22.214.120:28800/v2/repository/index
#curl -X POST http://172.22.214.120:28800/v2/repository/models/codellama-7b-instruct-hf/load -v

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, Dict, List, Optional
import os
import uuid
import requests
class TritonLLM3(LLM):

    @property
    def _llm_type(self) -> str:
        return "tritonllm3"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "CustomChatModel",
        }
        
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        #print("staring")
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        triton_url: str = os.environ["TRITON_LLM_ENDPOINT"]
        #trace_id: str = str(run_manager.parent_run_id)
        #span_id: str = str(run_manager.run_id)

        payload = {
            "text_input": prompt,
            "max_tokens": 1500,
            "temperature": 0.0,
            "stream": False
        }    

        ret = requests.post(
            triton_url,
            json=payload,
            #timeout=10,
            #headers= header_trace,
        )
        print(ret)
        res = ret.json()
        query_response = res["text_output"]

        return query_response