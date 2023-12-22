chat_response = chat_completion_request(
    conversation, tools=tools
)

for response in chat_response:
    print(response)

('id', 'chatcmpl-8XlYfragHjqoQRnqToP2zvjcVilil')
('choices', [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Sure, can you please provide me with your current location?', role='assistant', function_call=None, tool_calls=None))])
('created', 1703058329)
('model', 'gpt-3.5-turbo-0613')
('object', 'chat.completion')
('system_fingerprint', None)
('usage', CompletionUsage(completion_tokens=13, prompt_tokens=191, total_tokens=204))


# stream response (single chunk)
ChatCompletionChunk(id='chatcmpl-8XmStyttR2IHER9qc9hJp89KjrdYQ', choices=[Choice(delta=ChoiceDelta(content=None, function_call=None, role=None, tool_calls=None), finish_reason='stop', index=0, logprobs=None)], created=1703061815, model='gpt-3.5-turbo-0613', object='chat.completion.chunk', system_fingerprint=None)

# non-stream response
ChatCompletion(id='chatcmpl-8XmWdNPxxzC1i7jPNBDK09aBXeGNK', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Sure, I can help you with that. Could you please provide me with your current location?', role='assistant', function_call=None, tool_calls=None))], created=1703062047, model='gpt-3.5-turbo-0613', object='chat.completion', system_fingerprint=None, usage=CompletionUsage(completion_tokens=20, prompt_tokens=191, total_tokens=211))

for both pieces, finish_reason is still stop
I think I can just add up the pieces and call it a day as {'role':'assistant', '}