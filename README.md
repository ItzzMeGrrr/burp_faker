# Burp Faker

**Author:** Bhavin Vasara  
**Github:** [github.com/itzzmegrrr](https://github.com/itzzmegrrr)

---

## Table of Contents

- [Overview](#overview)  
- [Installation](#installation)  
- [Usage](#usage)  
  - [Placeholder Format](#placeholder-format)  
  - [Examples](#examples)  
- [Features](#features)  
- [Context Menu](#context-menu)  
- [License](#license)  

---

## Overview

Burp Faker helps you generate unique or custom fake data directly in Burp Suite requests. Many web scanners and extensions fail when requests reuse the same data repeatedly, or servers reject duplicate/invalid inputs. Unlike Postman or Insomnia, Burp does not have built-in support for per-request dynamic fake data. This extension solves that problem.

With Burp Faker, you can replace request body, headers, and URL parameters with:

- Random UUIDs  
- Alphanumeric, alphabetic, upper/lowercase, numeric, or custom-character strings  
- Regex-based strings (via `rstr` library)  

Each placeholder is replaced **independently**, and you can optionally assign **tags** to reuse the same value across multiple placeholders of the same type.

---


## Installation

> NOTE: Since Burp uses Jython for Python extensions, and Jython only supports Python 2.7, we need to manually add the `rstr` library to the same folder as the extension file. Therefore, we have the following two options for installation:

### Option 1: With regex support (manual from repo)

1. Clone this repository:

```bash
git clone https://github.com/itzzmegrrr/burp-faker.git
````

2. Make sure **Jython 2.7** is installed (required for Burp extensions).
3. In Burp Suite, go to **Extensions → Add → Extension Type: Python**, and load `burp_faker.py` from the cloned folder.

> Regex placeholders (`{{burp_faker.regex(...)}}`) will work out of the box since `rstr` is included in the repo.

---

### Option 2: Without regex support (BApp Store)

1. Open Burp Suite → **Extensions → BApp Store**
2. Search for **Burp Faker** and click **Install**

> In this mode, regex placeholders will not work, but all other fake data types are fully functional.


---

## Usage

### Placeholder Format

```
{{burp_faker.<type>(<length_or_charset_or_regex>, tag=<optional_tag>) }}
```

* `<type>`: `uuid`, `alphanumeric`, `alpha`, `lower`, `upper`, `numeric`, `custom`, `regex`
* `<length>`: Number of characters to generate (for string types)
* `<charset>`: For `custom`, the set of characters to use
* `<regex>`: For `regex` type
* `<optional_tag>`: Reuse the same value across multiple placeholders of the same type

### Examples

**Unique values**

```text
{{burp_faker.uuid()}}
{{burp_faker.alpha(10)}}
{{burp_faker.numeric(5)}}
```

**Reusing the same value with a tag**

```text
{{burp_faker.uuid(tag=session)}}
{{burp_faker.alpha(5, tag=session)}}
{{burp_faker.alpha(10, tag=session)}}  # Will slice from the longest alpha(10) value
```

**Custom charset**

```text
{{burp_faker.custom(10, abc123!@#)}}
```

**Regex**

```text
{{burp_faker.regex([a-z]{3}[0-9]{2})}}
```

**Notes:**

* Tagging is **per type**: a UUID tag is independent from an alpha tag with the same name.
* When multiple placeholders of the same type share a tag, the **longest requested length** is used, and shorter ones are sliced from it.
* Regex values are always generated uniquely and do **not** support tags or length slicing.
* Invalid placeholders output `INVALID_PLACEHOLDER` without slicing.

---

## Features

* Replace placeholders in **request body, headers, and URL parameters**
* Supports **UUID, alpha, alphanumeric, numeric, upper/lowercase, custom charset, and regex**
* **Optional tagging** to reuse the same value across multiple placeholders of the same type
* Each placeholder is independent and can be **unique or repeated** based on tags
* Context menu integration for **easy insertion** of placeholders
* Logs all replacements in Burp output for transparency

---

## Context Menu

Right-click a request in Burp and choose from:

* Insert UUID
* Insert alphanumeric
* Insert alpha, lower, upper, numeric
* Insert custom charset string
* Insert regex pattern

The placeholder is inserted at the selection and will be replaced automatically when the request is sent.

---

## License

MIT License
