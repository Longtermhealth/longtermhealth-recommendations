"""Setup configuration for LTH Recommendations system"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lth-recommendations",
    version="0.1.0",
    author="LongTermHealth",
    author_email="info@longtermhealth.com",
    description="A rule-based recommendation system for personalized health action plans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Longtermhealth/longtermhealth-recommendations",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "lth-recommendations=src.app:app",
        ],
    },
)