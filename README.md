# Routed Mixture of LLMs - MoLLMR
MoLLMR is a Mixture of LLMs with routing capabilities. This solution is typically referred to as a Mixture of Agents, or MoA for short. This includes worker LLMs that answer the same question, and an aggregate model that combines the individual answers into a final response that can often outperform the response from a single LLM.

MoLLMR can also use a routing model. If there are multiple mixtures defined with descriptions, it can attempt to select the best mixture suited to each request.

MoLLMR is currently only compatible with OpenAI compatible APIs, and hosts an OpenAI compatible API itself.

MoLLMR is also currently only a proof of concept and a work in progress. It is not ready for production workloads.

## Getting Started
```bash
# install requirements
pip install -r requirements.txt

# copy the example config and customize it to your needs
cp example-config.yaml config.yaml
```

## Usage
```bash
# start server
sh run.sh
```

```bash
# make a request to the server
curl http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{ 
  "model": "router",
  "messages": [ 
    { "role": "system", "content": "You are a helpful AI assistant." },
    { "role": "user", "content": "Please tell me a joke." }
  ], 
  "temperature": 0.7, 
  "max_tokens": -1,
  "stream": false
}'
```

## Roadmap
- [x] OpenAI compatible API
- [x] Configuration (model, base url, keys for workers and aggregate)
- [x] Allow single model bypass without aggregate prompting
- [ ] Customizable aggregate prompt(s)
- [ ] Customizable worker prompts?
- [ ] Customizable system prompts
- [ ] Customizable router prompt
- [ ] /models endpoint
- [ ] Support more options other than OpenAI compatible endpoints
- [x] OpenAI compatible API with streaming for final response
- [x] Router to have a base llm dynamically select from different mixtures with different strengths
- [ ] Router to have a base llm dynamically select from different models to build a mixture best suited to answer the prompt
