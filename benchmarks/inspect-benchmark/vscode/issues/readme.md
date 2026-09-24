# VS Code Model-Picker Limitation

This folder records an observed limitation when using small local models through
VS Code Chat. See the [detailed finding](vscode-model-picker-tool-calling-findings.md)
for the test evidence.

## Documented Limitation

- The [VS Code language-model documentation](https://code.visualstudio.com/docs/agent-customization/language-models#_add-a-model-from-a-built-in-provider)
  says that a model used with agents in chat must support tool calling; otherwise,
  it is not shown in the model picker.
- The [VS Code agent-harness documentation](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses#_how-a-harness-differs-from-other-agent-concepts)
  lists Ask as an agent role alongside Agent, Plan, and custom agents.

Together, these constraints explain why setting `toolCalling: false` can remove a
custom local model from the picker, including when trying to use Ask. This matches
the current documentation rather than demonstrating a bug.

## Possible Feature Request

A feature request could ask VS Code to expose non-tool-calling models in a
question-only role. Tiny local models could then inspect and explain code without
receiving tool schemas or tool-calling grammar, similar to chat workflows in the
Continue extension. Avoiding that payload can make prompt processing practical
for models that otherwise loop, reject the grammar, or exceed useful context
limits. This should be proposed as a new capability rather than a bug report.