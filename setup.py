from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Smart-code-review-bot",
    version="0.1.0",
    author="PRWise Check Team",
    author_email="asif.masood@dellteam.com, shobhit.tiwary@dellteam.com, " \
    "suchithra.k@dellteam.com, vojjala.shivani@dellteam.com",
    description="A GitHub code review bot using Ollama AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/smartcode0108/smart_code_review",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["ollama-code-review-bot=ollama_code_review_bot.main:main"],
    },
    include_package_data=True,

)

