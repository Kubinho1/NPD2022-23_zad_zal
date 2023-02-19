import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
 long_description = fh.read()
setuptools.setup(
 name="zad_zal", 
 version="0.0.1",
 author="JB", # <-- update
 url="https://github.com/Kubinho1/NPD2022-23_zad_zal",
 packages=setuptools.find_packages(),
 classifiers=[
 "Programming Language :: Python :: 3",
 "License :: OSI Approved :: MIT License",
 "Operating System :: OS Independent",
 ],
 python_requires='>=3.6',
 py_modules=["main", "extra_functions"]
)
