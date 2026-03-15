### Starting service

in service/src/:
```uv run taskiq worker app.tkq:broker app.tasks --reload```
```uv run taskiq scheduler app.broker:scheduler```