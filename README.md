# JSON Annotator

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/nlohmann/json/master/LICENSE.MIT)
[![GitHub Issues](https://img.shields.io/github/issues/valery-arzumanov/json-annotator.svg)](https://github.com/valery-arzumanov/json-annotator/issues)
[![Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/valery-arzumanov/json-annotator/main/pyproject.toml)](https://www.python.org)

- [Preamble](#preamble)
- [Design goals](#design-goals)
- [Installation](#installation)
- [Basic usage](#basic-usage)
- [Errors](#errors)
    - [Internal problems](#internal-problems)
    - [Invalid input](#invalid-input)
    - [Discouraged practices](#discouraged-practices)
        - [Items of different types in array](#items-of-different-types-in-array)
        - [Boolean values or nulls in array](#boolean-values-or-nulls-in-array)
- [References](#references)

## Preamble
There occur certain situations, when it is necessary to have a full structure of a JSON document of a particular kind. This structure should meet the following conditions:
- all nodes should be enumerated, thus constituting a complete list
- all values should be provided with a type hint (with a minor exception described below)

## Design goals
This library serves to draw up the structure of a JSON document. The output of the annotation is a list of strings, each of which consists of three parts:
1. JSON pointer-like string (`<JP>`)
2. a separator (`<SE>`)
3. a type hint (`<TH>`)

The resulting string has the following format: `<JP><SE><TH>`. Mind the absence of **spaces** between the parts — if they are needed, they should be added **manually**.

> [!NOTE]
> *JSON Pointer* defines a string syntax for identifying a specific value within a JavaScript Object Notation document (for more information see [RFC 6901](https://www.rfc-editor.org/info/rfc6901)).
> To gain a better understanding of the concept more context is needed. Have a look at this snippet:
> ```json
> {
>     "A":
>     {
>         "B": [1, 2]
>     },
>     "C":
>     {
>         "D": "E"
>     }
> }
> ```
> On the basis of the information provided in [RFC 6901](https://www.rfc-editor.org/info/rfc6901), it is possible to write down 7 JSON pointers for this snippet: `<empty>` (the whole document) `/A`, `/A/B`, `/A/B/0` (= 1), `/A/B/1` (= 2), `/C`, `/C/D` (= "E").
>
> The annotation performed by this library has several distinctions from this notation:
> - there is no empty string, corresponding to the whole document, because its type is always the same — it is JSON object
> - pointer-like strings **do not** start with a node separator, which marks the root
> - a node separator may be both an arbitrary character and a string of characters of an arbitrary length
> - there are no pointer-like strings, corresponding to the indexed array items — arrays are seen as a whole node and the individual items are not typed
>
> Taking into the consideration the above, it is possible to figure out that the annotator will yield only 4 pointer-like structures: `A`, `A/B`, `C`, `C/D`.

## Installation
To install the package it is necessary to perform the following steps: 
1. Make sure that your `Python` interpreter's version meets the requirements.
2. Clone the repository.
3. Launch system terminal and `cd` into the directory, where the repository was cloned prior.
4. (*optional*) Create a virtual environment.
5. To install from the wheel run `python -m pip install .` (mind the dot). Whether it fails, consider upgrading `pip`.

Generally, the package should be installed without any problems. If it does not, you are welcome to [report a bug](https://github.com/valery-arzumanov/json-annotator/issues/new/choose).

## Basic usage
Library basic usage is rather simple. Here is a brief example:
```python
>>> import json
>>> from json_annotator import JsonAnnotator, ErrorData, ErrorCode
>>>
>>> input_data: str = '{"A": { "B": [1, 2] }, "C": { "D": "E" } }'
>>> json_content: dict = json.loads(input_data)
>>> annotator: JsonAnnotator = JsonAnnotator("/", " -> ")
>>> result: ErrorData = annotator.build_node_reprs(json_content)
>>> if result.code == ErrorCode.OK:
...     print(annotator.get_node_repr_list())
...     
['A -> object', 'A/B -> intArray', 'C -> object', 'C/D -> str']
```

## Errors
Before describing potential issues, which a user can encounter, it is important to note that if an error occurs, the annotator's node representation list will be cleared, even if the document is only partially malformed. The idea behind this is the same with the one, lying under JSON linting — the document should be valid as a whole. Thus, it is always worth checking the result of the annotation and making sure that it is `ErrorCode.OK` (`0`) before proceeding. If it is not, it is possible to get the error message using `ErrorData.get_error_message()`:
```python
>>> import json
>>> from json_annotator import JsonAnnotator, ErrorData, ErrorCode
>>>
>>> input_data: str = '{"A": { "B": [true, false] }, "C": { "D": "E" } }'
>>> json_content: dict = json.loads(input_data)
>>> annotator: JsonAnnotator = JsonAnnotator("|", ": ")
>>> result: ErrorData = annotator.build_node_reprs(json_content)
>>> if result.code == ErrorCode.OK:
...     print(annotator.get_node_repr_list())
... else:
...     print(result.get_error_message())
Error occurred. Problematic entity: "A|B|0"
```

### Internal problems
An internal error occurs if the annotator encounters an entity with an unknown type — as long as it does not know what to do with it, `ErrorCode.INTERNAL_FATAL_ERROR` (`2`) is returned right away. This situation ought to be reported via [creating an issue](https://github.com/valery-arzumanov/json-annotator/issues/new/choose) in the project repository.

### Invalid input
If the JSON document, passed to the annotator, is not valid, the annotator will return `ErrorCode.INCORRECT_INPUT_FORMAT` (`1`).

### Discouraged practices
JavaScript Object Notation is rather intuitive. Syntax rules, which should not be broken, are neither numerous nor difficult to pick up (see [RFC 8259](https://www.rfc-editor.org/info/rfc8259) for details). The construction of JSON objects and the nodes with values of, so to speak, *"basic types"* (like strings, numbers or booleans) do not generally pose a challenge, whether one abides by the above-mentioned rules, while arrays require a second thought sometimes.

What follows is not prohibited by the standard, but may be error-prone or lead to misinterpretation or bad readability.

#### Items of different types in array
Consider the following snippet:
```json
{
    "objectData": [100, 100, "ComboBox", "Levels"]
}
```
What does a pair `(100, 100)` correspond to? Is it *x* and *y* or *width* and *height*? What about "Levels"? Is it object's name, first line or something else? If the structure remains intact, it will be difficult enough to come up with an array name, which will resolve the ambiguity. It is better to transform the array into a JSON object, which will be more illustrative:
```json
{
    "objectData": 
    {
        "X": 100,
        "Y": 100,
        "objectType": "ComboBox",
        "objectTitle": "Levels"
    }
}
```
This looks much better, doesn't it? A decent guide on JSON construction will point out that **arrays should be used for a series of items, serving for a unified, understandable purpose** (like weekdays, for instance). Thus, a good practice is to put items of **the same** type into a JSON array — otherwise the original intent may become obscured. The annotator will return `ErrorCode.DIFFERENT_ARRAY_ITEM_TYPES` (`3`), if it encounters an array with items of different types.

#### Boolean values or nulls in array
Consider the following 2 snippets:
```json
{
    "objectFlags": [false, true, true]
}
```
```json
{
    "objectFlags": [null, null, null]
}
```
Albeit these arrays are completely valid from a syntax perspective, it is impossible to understand, what the values correspond to. Hence, one can get confused and make a mistake, because the order of values in this case may be only memorized. It is a good idea to transform these arrays into JSON objects as well. The annotator will return `ErrorCode.NULLS_IN_ARRAY` (`4`) and `ErrorCode.BOOLS_IN_ARRAY` (`5`) if there are nulls or boolean values in the input JSON array, respectively. 

## References
1. Bryan, P., Ed., Zyp, K., and M. Nottingham, Ed., "JavaScript Object Notation (JSON) Pointer", RFC 6901, DOI 10.17487/RFC6901, April 2013, <https://www.rfc-editor.org/info/rfc6901>.
2. Bray, T., Ed., "The JavaScript Object Notation (JSON) Data Interchange Format", STD 90, RFC 8259, DOI 10.17487/RFC8259, December 2017, <https://www.rfc-editor.org/info/rfc8259>.