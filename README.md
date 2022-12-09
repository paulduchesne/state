# State

[State](https://github.com/paulduchesne/state) is a collection of scripts and data structures intended to facilitate the generation of personal linked data, following W3C semantic web standards. These statements are encrypted by default and can be selectively exposed. There is significant overlap with [Solid](https://solidproject.org/), and there is a possibility that this project will be retired in the future to work with that protocol instead.

The name is derived from "state" as a verb, synonymous with "assert" or "declare", but also has other linguistic implications.

This repository currently comprises a dedicated Python module for programmatic use, with the intention to eventually graduate to a web application.

`state.me('paul duchesne', '1986-04-14')`

An important initial step is to define the individual who will be making all resulting statements. Required fields are a name and a date of birth. Date of birth is currently mandatory for all individuals as an excellent (although not collision infallible) method of disambiguation.

`state.person('philip kindred dick', '1928-12-16')`

Other individuals can be defined, although their initial URI will be contained under the author's namespace. A useful function would be to identify where individuals have defined themselves using this protocol elsewhere, and "adopt" their own expressed identity.

`state.file(pathlib.Path.home() / '02.flac')`

One of the more interesting aspects of this prototype is that files can also be stored in the resulting graph, both metadata around the file and the file payload stored as an encrypted base64 string. Given the comparatively large size of these specific statements, there is currently a shallow/deep flag to indicate where the encrypted triples contain file data.

`state.decrypt_all()`

The entire local graph (minus file data) can be decrypted with a single function call.
