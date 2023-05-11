from setuptools import setup, find_packages  
  
setup(  
    name='MelodieTable',  
    version='0.1.0',  
    packages=find_packages(),  
    install_requires=[  
        'sqlalchemy',  
        'openpyxl',  
        'pymysql'
    ],  
    entry_points={  
        'console_scripts': [  
            'melodie_table = melodie_table.scripts.main:main',  
        ],  
    },  
)