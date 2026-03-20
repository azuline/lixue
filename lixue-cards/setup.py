import setuptools

with open("lixue_cards/.version") as f:
    version = f.read().strip()

setuptools.setup(
    name="lixue-cards",
    version=version,
    python_requires=">=3.12.0",
    author="blissful",
    author_email="blissful@sunsetglow.net",
    license="AGPL-3.0-or-later",
    entry_points={"console_scripts": ["lixue-cards = lixue_cards.__main__:main"]},
    packages=["lixue_cards"],
    package_data={"lixue_cards": ["py.typed", ".version"]},
    install_requires=["click", "anki"],
)
