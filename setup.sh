# 1. ENVIRONMENT -> pip install -r < Requirement file path > 
pip install -r "requirements.txt"

# *Make sure the right DATABASE NAME in setting SQLALCHEMY_DATABASE_URI in constant.py
# 2. DATABASE
# 3. DATA TO DATABASE  
python recreate.py

# *Want to delete all TABLE to test ? Sql query : drop table <table_name> cascade;