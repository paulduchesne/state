# STATE

**Introduction**

Inspired as much by Annie Ernaux and Karl Ove Knausgaard as by Jer Thorp or Tim Berners-Lee, State is the latest iteration of a longstanding interest in modelling data into a personal knowledge graph. This is intended as a technical exercise, potentially personally useful, and as a counterpoint to the clandestine accumulation of such data by others.

The term "state" refers both to the representation of "states" of myself, and as a platform where I can "state" information.

**Utilities**

There are a number of helper functions for adding data to the graph.

```python
# add a person.

state.person(
    label="Adelheid Heftberger", 
    comment="Austrian researcher.", 
    member="Bundesarchiv", 
    wikidata="Q42369365",
    )

# add a location.

state.location(
    label="Rabat", 
    comment="Capital city of Morocco.", 
    wikidata="Q3551",
    )
```

**Example**

→ [Paul Duchesne](https://paulduchesne.github.io/state/resource/0ef53722-52ca-49c8-873d-3549a74914e8)

**License**

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)

