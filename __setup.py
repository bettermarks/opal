import urllib.parse
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_requirements_file(path):
    with open(path) as f:
        for line in f.read().splitlines():
            # sanitize line
            line, *_ = line.split(" ")
            line, *_ = line.split(";")

            # ignore comments and pip cli args
            if line.startswith("-") or line.startswith("#"):
                continue

            # convert pip git format to setuptools
            if line.startswith("git+ssh://"):
                p = urllib.parse.urlparse(line)
                # get package name
                _, package_name = p.fragment.split("egg=")
                yield f"{package_name} @ {p.scheme}://{p.netloc}{p.path}"
            else:
                yield line


setuptools.setup(
    name="licensing",
    version="0.0.1",
    author="bettermarks GmbH",
    author_email="bmdevops@bettermarks.com",
    description="Licensing Service.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    include_package_data=True,
    package_dir={"": "src"},
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#find-namespace-packages
    packages=setuptools.find_namespace_packages(where="src"),
    entry_points={"console_scripts": []},
    # we locked use req txt for final dist
    install_requires=list(parse_requirements_file("requirements.txt")),
    extras_require={
        "tests": list(parse_requirements_file("requirements-dev.txt")),
        "export": list(parse_requirements_file("requirements-export.txt")),
    },
)
