# Python PKG-INFO Stats

| Notebook | Link |
|:--|:--|
| `Project-URL` | [![Binder](https://mybinder.org/badge_logo.svg)][project-url]

[project-url]: https://mybinder.org/v2/gh/jimustafa/py-pkg-info-stats/main?urlpath=voila%2Frender%2Fbuild%2Fproject-url.ipynb

This project uses information available through
  [libraries.io](https://libraries.io) and [PyPI](https://pypi.org)
  to understand the existing conventions for Python package metadata.
The [SourceRank](https://docs.libraries.io/overview.html#sourcerank) metric is used to identify the "top" Python packages on PyPI,
  and the PyPI project sites (e.g., https://pypi.org/project/numpy) are read and parsed to extract some of the `PKG-INFO`.
Currently, there is a notebook for looking at variation in `Project-URL` specifications,
  with notebooks for other metadata items hopefully to follow.

## Related PEPs and Other Links

- [PEP 241](https://peps.python.org/pep-0241) — Metadata for Python Software Packages
- [PEP 314](https://peps.python.org/pep-0314) — Metadata for Python Software Packages 1.1
- [PEP 345](https://peps.python.org/pep-0345) — Metadata for Python Software Packages 1.2
- [PEP 566](https://peps.python.org/pep-0566) — Metadata for Python Software Packages 2.1
- [PEP 621](https://peps.python.org/pep-0621) — Storing project metadata in pyproject.toml
- [PyPA Tutorial: Packaging](https://packaging.python.org/en/latest/tutorials/packaging-projects/#configuring-metadata) — Configuring metadata
