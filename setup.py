from setuptools import setup

setup(
    name='AudioBat',
    version='1.0.0',
    description='AudioBat TPI ',
    long_description='Proyecto Integrador final',
    long_description_content_type='text/markdown',
    author='AE',
    author_email='alejandroescobar264@gmail.com',
    py_modules=['lanzador'],
    entry_points={'console_scripts': 'lanzador = lanzador:Lanzador.ejecutar'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)