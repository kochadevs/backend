<h3 align="center">KOCHA AI Application API</h3>

<div align="center">

  ![Status](https://img.shields.io/badge/status-active-success.svg)
  ![GitHub issues](https://img.shields.io/github/issues/?color=yellow)
  ![GitHub pull requests](https://img.shields.io/github/issues-pr/?color=success)
  [![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](/LICENSE)


</div>

---

<p align="center"> Backend API for KochaAI Application
    <br> 
</p>

## 📝 Table of Contents
- [TODO](#todo)
- [About](#about)
- [Getting Started](#getting_started)
- [Running the tests](#tests)
- [Project Structure](#structure)
- [Contributing](#contributing)
- [Usage](#usage)
- [Built Using](#built_using)
- [Team](#team)

## Todo <a name = "todo"></a>
See [TODO](./docs/TODO.md)

## About <a name = "about"></a>
This is the Kocha AI application for managing professional career roadmap and mentorship, etc

## 🏁 Getting Started <a name = "getting_started"></a>
These are the instructions to get the project up and running on your local machine for development and testing purposes.

### Prerequisites
- PIP: Dependency manager for Python.
- Supabase: A managed service to support backend.
- Python 3.12^: The Python programming language.
- Flake8: An auto-formatter for Python code.
- Mypy: Static Type checking 
- Cliff - Change release management 


### Setting up a development environment
### Step 1: Clone the repository

```bash
https://github.com/kochadevs/backend.git
```

or with GithubCLI
  
```bash
gh repo clone kochadevs/backend
```

### step 2: Create a virtual environment

```bash
virtualenv kochaenv
```
OR by using the virtualenvwrapper
```bash
  mkvirtualenv kochaenv
```
Activate the virtual environment with 
```bash
  source kochaenv/bin/activate
```

#### Step 3: Install dependencies

```
pip install -r requirements.txt
```

> Note to add a package to the project, run

```bash
pip install <package-name>
```
