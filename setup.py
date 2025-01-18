from setuptools import setup, find_packages

setup(
    name="interviewers",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=[
        "pydantic>=2.5.0",
        "fastapi>=0.104.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "asyncio>=3.4.3",
        "aiohttp>=3.9.0",
        "tenacity>=8.2.0",
        "prometheus-client>=0.17.0",
        "motor>=3.3.1"  # MongoDB async driver
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.9.1',
            'isort>=5.12.0',
            'mypy>=1.5.1',
        ]
    },
    author="AI Interview System Team",
    author_email="team@example.com",
    description="An AI-powered interview system with MongoDB persistence",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
    ],
)
