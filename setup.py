from setuptools import setup, find_packages

setup(
    name="prime-number-checker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "gmpy2==2.1.5",
        "numpy==1.24.3",
        "click==8.1.7",
        "tqdm==4.66.1",
    ],
    extras_require={
        "gpu": ["cupy-cuda12x==12.3.0", "pycuda==2022.2.2"],
        "dev": ["pytest==7.4.3", "pytest-cov==4.1.0"],
    },
    entry_points={
        "console_scripts": [
            "prime-check=prime_checker.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Prime Number Project",
    description="A high-performance prime number checker for very large numbers",
)