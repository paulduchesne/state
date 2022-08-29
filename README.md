# State

[State](https://github.com/paulduchesne/state) is a collection of scripts and data structures intended to facilitate the generation of personal linked data, following W3C semantic web standards. These statements are encrypted by default and can be selectively exposed. There is significant overlap with [Solid](https://solidproject.org/), and there is a possibility that this project will be retired in the future to work with that protocol instead.

The name is derived from "state" as a verb, synonymous with "assert" or "declare", but also has other linguistic implications.

This repository currently comprises a collection of Python scripts, with the intention to eventually migrate to a dedicated node.js web app.

#### about_me.py

The first step of the process is to declare yourself as an entity, who will be responsible for the authorship of all future claims.

Two datapoints are expected, a name and a date of birth. The script automatically generates a UUID which will represent the first-person subject, and provide a URI namespace.