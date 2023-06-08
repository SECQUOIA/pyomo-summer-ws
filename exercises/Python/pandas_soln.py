# Your colleague wants to build a classifier that will identify types of bears,
# but is having trouble importing data for her project. Lucikly, you know about
# pandas. No, not the fluffy black and white things, the python data
# manipulation package.

# The file bears-are-bears.csv contains a human-generated categorization of
# several bear specimens obtained by underpaying undergraduate students to
# collect data. Please import the file and display it to the console to verify
# that it matches your expectations.

import pandas

# df = pandas.read_csv(--CODE TO IMPORT HERE--)
# print(df)

# Answer:

df = pandas.read_csv('bears-are-bears.csv', index_col=0)
print(df)

# Your colleague wants to have an alphabetically sorted unique list of all the
# bear types. Generate this from the pandas DataFrame.

# sorted_bears = --CODE HERE TO CREATE UNIQUE SORTED LIST--
# print("Sorted bears list:")
# print(sorted_bears)

# Answer:

sorted_bears = sorted(df['Bear Type'].unique().tolist())
print("Sorted bears list:")
print(sorted_bears)
