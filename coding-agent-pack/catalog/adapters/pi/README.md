# Pi Adapter

The installer converts core agents into Pi `SKILL.md` files and installs core skills under the selected Pi scope:

```text
Project: .pi/skills/ and .pi/extensions/
Global:  ~/.pi/agent/skills/ and ~/.pi/agent/extensions/
```

It does not copy authentication, settings, or model catalogs. The local-model extension checks the project `.pi/models.json` first and the global Pi agent directory second.
