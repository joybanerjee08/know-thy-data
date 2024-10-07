import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import difflib

genai.configure(api_key=st.secrets["gemini_api_key"])

def find_closest_match(input_string, string_list):
  """
  Finds the closest matching string in a list to the given input string.

  Args:
    input_string: The input string to be matched.
    string_list: A list of strings to compare against.

  Returns:
    The closest matching string in the list, or None if no close match is found.
  """
  # Find the closest match using difflib.get_close_matches
  if input_string in string_list:
    return input_string

  closest_match = difflib.get_close_matches(input_string, string_list, n=1)[0]

  # Calculate the ratio of similarity between the input string and the closest match
  similarity_ratio = difflib.SequenceMatcher(None, input_string, closest_match).ratio()

  # Set a threshold for similarity
  similarity_threshold = 0.8

  # Return the closest match if the similarity ratio is above the threshold
  if similarity_ratio > similarity_threshold:
    return closest_match
  else:
    return None

def any_two_not_none(variables):
  """
  Checks if any two variables in the given list are not None.

  Args:
    variables: A list of variables.

  Returns:
    True if at least two variables are not None, otherwise False.
  """

  count = 0
  for variable in variables:
    if variable is not None:
      count += 1
      if count >= 2:
        return True
  return False

def col_to_prompt(col,idx,typ,desc):
    if col != None:
        if desc != "":
            return f"COLUMN {idx} NAME: {col} | COLUMN {idx} TYPE: {typ} | COLUMN {idx} DESCRIPTION: {desc}"
        else:
            return "error"
    return ""

def main():
    st.set_page_config(page_title="Know Thy Data", page_icon="knowthydata.jpg", layout="wide", initial_sidebar_state="auto", menu_items=None)
    st.title("Know Thy Data")
    st.image("knowthydata.jpg",width=256)
    st.markdown("**Know Thy Data is an innovative application that leverages the power of Google Gemini to provide comprehensive data analysis.** Users simply input their problem statement, data description, and up to 5 columns (including data type and description). Gemini then processes this information, extracting valuable insights and generating a variety of charts to visualize the data effectively. This intuitive tool empowers users to gain a deeper understanding of their datasets and make informed decisions based on data-driven analysis.")
    st.subheader("Tips to use:")
    st.markdown("1.Ensure your CSV file has headers")
    st.markdown("2.No Missing values should be present")
    st.markdown("3.Numerical columns (Discreet or Continuous) must contain only numbers, not spaces or text")
    st.markdown("4.Output depends on how well defined the problem statement, data description and column descriptions are")
    st.markdown("5.Problem statement and Data description cannot be greater than 1500 words and column description cannot be greater than 100 words")
    st.markdown("6.Try not to use any special characters in your header of the csv file, only alphabets,digits,period,hyphen and underscore")
    st.divider()

    uploaded_file1 = st.file_uploader("Choose a CSV file with headers", type=["csv"])

    file_uploaded = False

    if uploaded_file1 is not None:
        with open("./"+uploaded_file1.name, "wb") as f:
            f.write(uploaded_file1.getvalue())

        df = pd.read_csv("./"+uploaded_file1.name)

        st.success("CSV uploaded and saved successfully!")
        st.write(uploaded_file1.name)

        st.subheader("Tell the AI about your problem statement and data given", divider=True)

        problem_statement = st.text_area("Describe the problem statement you're solving with this data", value="", max_chars=1500,key="problem")

        data_desc = st.text_area("Describe the data you're uploading", value="", max_chars=1500,key="data")
        file_uploaded = True

        st.subheader("Select upto 5 columns and describe them", divider=True)

        grid = st.columns(5)

        st.markdown('<style>.stSelectbox > div { width: 100% !important; }</style>', unsafe_allow_html=True)
        col1,col2,col3,col4,col5,type1,type2,type3,type4,type5,desc1,desc2,desc3,desc4,desc5 = None,None,None,None,None,None,None,None,None,None,None,None,None,None,None
        with grid[0]:
            col1 = st.selectbox('Select 1st column',df.columns.tolist(),placeholder="Select Column",index=None, key = "col1")
            if col1 != None:
                type1 = st.selectbox('What type of Data is this ?',('Nominal', 'Ordinal', 'Discrete', 'Continuous','Boolean','Date','Time','Date and Time','Interval','Constant'), key = "type1")
                desc1 = st.text_input("Describe this column", value="", max_chars=100, key = "desc1")
        with grid[1]:
            col2 = st.selectbox('Select 2nd column',df.columns.tolist(),placeholder="Select Column",index=None, key = "col2")
            if col2 != None:
                type2 = st.selectbox('What type of Data is this ?',('Nominal', 'Ordinal', 'Discrete', 'Continuous','Boolean','Date','Time','Date and Time','Interval','Constant'), key = "type2")
                desc2 = st.text_input("Describe this column", value="", max_chars=100, key = "desc2")
        with grid[2]:
            col3 = st.selectbox('Select 3rd column',df.columns.tolist(),placeholder="Select Column",index=None, key = "col3")
            if col3 != None:
                type3 = st.selectbox('What type of Data is this ?',('Nominal', 'Ordinal', 'Discrete', 'Continuous','Boolean','Date','Time','Date and Time','Interval','Constant'), key = "type3")
                desc3 = st.text_input("Describe this column", value="", max_chars=100, key = "desc3")
        with grid[3]:
            col4 = st.selectbox('Select 4th column',df.columns.tolist(),placeholder="Select Column",index=None, key = "col4")
            if col4 != None:
                type4 = st.selectbox('What type of Data is this ?',('Nominal', 'Ordinal', 'Discrete', 'Continuous','Boolean','Date','Time','Date and Time','Interval','Constant'), key = "type4")
                desc4 = st.text_input("Describe this column", value="", max_chars=100, key = "desc4")
        with grid[4]:
            col5 = st.selectbox('Select 5th column',df.columns.tolist(),placeholder="Select Column",index=None, key = "col5")
            if col5 != None:
                type5 = st.selectbox('What type of Data is this ?',('Nominal', 'Ordinal', 'Discrete', 'Continuous','Boolean','Date','Time','Date and Time','Interval','Constant'), key = "type5")
                desc5 = st.text_input("Describe this column", value="", max_chars=100, key = "desc5")

        prompt = "PROBLEM STATEMENT: "+problem_statement + "\n\n" + "DATA DESCRIPTION: " + data_desc
        
        if st.button("Get Insights"):
            if any_two_not_none([col1,col2,col3,col4,col5]):
                for idx,cols,typ,desc in zip([1,2,3,4,5],[col1,col2,col3,col4,col5],[type1,type2,type3,type4,type5],[desc1,desc2,desc3,desc4,desc5]):
                    if cols == None:
                        continue
                    output = col_to_prompt(cols,idx,typ,desc)
                    if output=='error':
                        st.error("You need describe your selected column !")
                        return
                    elif output != "":
                        prompt += "\n\n" + output + "\n\n" + "These are the columns of the data:"
                prompt += "\n\n" + """QUESTION: Based on the problem statement, data description and columns presented above, give me insights on how these columns can be useful to solve the problem statement given. 
Also tell me which type of chart would be insightful using the given columns in the following format : COLUMN 1 NAME + COLUMN 2 NAME = LINE CHART (Explanation of the chart). Use the exact column name given and don't add any new columns. The Chart Names must be "Line", "Bar", "Pie", "Scatter","Box". Don't use any other chart names.

Example:

PROBLEM STATEMENT: Figure out how the house prices are calculated and if features can be combined to create a better predictor.

DATA DESCRIPTION: Data contains 200 rows and 3 columns of house area, rooms, prices.

These are the columns of the data:

COLUMN 1 NAME: area | COLUMN 1 TYPE: Continuous | COLUMN 1 Description: Area of the house in square feet
COLUMN 2 NAME: rooms | COLUMN 2 TYPE: Discreet | COLUMN 2 Description: Number of rooms in the house
COLUMN 3 NAME: prices | COLUMN 3 TYPE: Continuous | COLUMN 3 Description: Price of the house

QUESTION: Based on the problem statement and columns presented above, give me insights on how these columns can be useful to solve the problem statement given. 
Also tell me which type of chart would be useful using given columns in the following format : COLUMN 1 NAME + COLUMN 2 NAME = LINE CHART (Explanation of the chart). Use the exact column name given and don't add any new columns. The Chart Names must be "Line", "Bar", "Pie", "Scatter","Box". Don't use any other chart names.

INSIGHT: House prices generally have direct correlation with number of rooms and area, so they can be used to predict the prices. Combining number of rooms and area into a single column might give a better correlation with the house price.

CHART: area + prices = Scatter (This chart will show correlation between area and prices of the house, area by itself may not give high correlation but combining it with other parameters might give a strong correlation)
rooms + prices = Scatter (This chart will show correlation between number of rooms and prices of the house, number of rooms may not be strong indicator of prices)
rooms = Pie (This chart displays which number of rooms are more frequent than the others, helping one identify the distribution)
-----------------------------------------------------------------
INSIGHT:

CHART:"""
                st.info("Generating Insights, please wait...")
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(
                    temperature=0.33,
                    # top_k=1,
                ))
                st.write(response.text)
                st.balloons()
                st.divider()

                charts = []
                for spe in response.text.split("\n"):
                    try:
                        output = spe.split("**")[1]
                        if "=" in output:
                            charts.append(output)
                    except:
                        print("error")
                
                for ch in charts:
                    fig=None
                    if "box" in ch.lower():
                        x_axis = find_closest_match(ch.replace("\"",'').split("+")[0].strip(),df.columns.tolist())
                        y_axis = find_closest_match(ch.replace("\"",'').split("=")[0].split("+")[1].strip(),df.columns.tolist())
                        if x_axis != None and y_axis != None:
                            fig = px.box(df, x=x_axis, y=y_axis)
                    if "scatter" in ch.lower():
                        x_axis = find_closest_match(ch.replace("\"",'').split("+")[0].strip(),df.columns.tolist())
                        y_axis = find_closest_match(ch.replace("\"",'').split("=")[0].split("+")[1].strip(),df.columns.tolist())
                        if x_axis != None and y_axis != None:
                            fig = px.scatter(df, x=x_axis, y=y_axis)
                    if "line" in ch.lower():
                        x_axis = find_closest_match(ch.replace("\"",'').split("+")[0].strip(),df.columns.tolist())
                        y_axis = find_closest_match(ch.replace("\"",'').split("=")[0].split("+")[1].strip(),df.columns.tolist())
                        if x_axis != None and y_axis != None:
                            fig = px.line(df, x=x_axis, y=y_axis)
                    if "bar" in ch.lower():
                        x_axis = find_closest_match(ch.replace("\"",'').split("+")[0].strip(),df.columns.tolist())
                        y_axis = find_closest_match(ch.replace("\"",'').split("=")[0].split("+")[1].strip(),df.columns.tolist())
                        if x_axis != None and y_axis != None:
                            fig = px.bar(df, x=x_axis, y=y_axis)
                    if "pie" in ch.lower():
                        if "x" in ch:
                            x_axis = find_closest_match(ch.replace("\"",'').split("+")[0].strip(),df.columns.tolist())
                            y_axis = find_closest_match(ch.replace("\"",'').split("=")[0].split("+")[1].strip(),df.columns.tolist())
                            if x_axis != None and y_axis != None:
                                fig = px.pie(df, names=x_axis, values=y_axis)
                        else:
                            x_axis = find_closest_match(ch.replace("\"",'').split("=")[0].strip(),df.columns.tolist())
                            if x_axis != None:
                                df1 = df.groupby([x_axis])[x_axis].count().reset_index(name='count')
                                fig = px.pie(df1, names=x_axis, values="count")
                    
                    if fig!=None:
                        st.subheader(ch.split("=")[0].strip(), divider=True)
                        st.plotly_chart(fig, use_container_width=True,key=ch)
                        st.divider()
                    
            else:
                st.error("You need to select atleast two columns and describe them !")
        
if __name__ == "__main__":
    main()