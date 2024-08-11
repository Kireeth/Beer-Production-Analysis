import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    layout = 'wide',
    page_title="Beer Production Analysis",
    page_icon="🍺", 
    initial_sidebar_state="expanded",
)

tab1, tab2 = st.tabs(["Charts", "Raw Data"])

@st.cache_data
def load_data(file_path, nrows=None):
    data = pd.read_csv(file_path, nrows=nrows)

    data['Brew_Date'] = pd.to_datetime(data['Brew_Date'])

    return data

data_sample = load_data(r"C:\Users\Kiree\Downloads\archive\brewery_data_complete_extended.csv", nrows=15000)

tab1.title('Beer Production Analysis')

st.sidebar.title('Filter Options')

beer_style_filter = st.sidebar.selectbox('Beer Style', data_sample['Beer_Style'].unique())
location_filter = st.sidebar.selectbox('Location', data_sample['Location'].unique())
data_source = st.sidebar.link_button(label="Data Source", url="https://www.kaggle.com/datasets/ankurnapa/brewery-operations-and-market-analysis-dataset?resource=download")
credits_dev = st.sidebar.text(body="Developed by Kireeth Karunakaran.")

filtered_data = data_sample[
    (data_sample['Beer_Style'] == beer_style_filter) &
    (data_sample['Location'] == location_filter)
]



tab2.subheader('Filtered Dataset')
tab2.write(filtered_data)


tab2.subheader('Summary Statistics of Filtered Data')
tab2.write(filtered_data.describe())

tab1.subheader('Quality Score Distribution')
tab1.caption("""
The boxplot below compares quality scores across different locations, useful for assessing location-specific quality variations.
""")

whisker_data = filtered_data.groupby('Location').Quality_Score.agg(
    lower_quartile=lambda x: x.quantile(0.25),
    upper_quartile=lambda x: x.quantile(0.75),
    min_val='min',
    max_val='max'
).reset_index()

whisker_data['iqr'] = whisker_data['upper_quartile'] - whisker_data['lower_quartile']

whisker_data['lower_whisker'] = whisker_data['lower_quartile'] - 1.5 * whisker_data['iqr']
whisker_data['upper_whisker'] = whisker_data['upper_quartile'] + 1.5 * whisker_data['iqr']

whisker_data['lower_whisker'] = whisker_data[['lower_whisker', 'min_val']].max(axis=1)
whisker_data['upper_whisker'] = whisker_data[['upper_whisker', 'max_val']].min(axis=1)

whisker_layer = alt.Chart(whisker_data).mark_rule(color='white').encode(
    y='Location:N',
    x= 'upper_quartile',
    x2='upper_whisker:Q'
)

whisker_layer2 = alt.Chart(whisker_data).mark_rule(color='white').encode(
    y='Location:N',
    x='lower_whisker:Q',
    x2='lower_quartile'
)

box_layer = alt.Chart(filtered_data).mark_boxplot(color="#FF5D50").encode(
    y=alt.Y('Location', title=""),
    x=alt.X('Quality_Score', title='Quality Score'),
    tooltip=['Location', 'Quality_Score']
)

combined_chart = box_layer + whisker_layer + whisker_layer2

tab1.altair_chart(combined_chart, use_container_width=True)

tab1.subheader('Sales/Volume vs. Bitterness')
tab1.caption("""
This scatter plot shows the relationship between bitterness levels and total sales over the total volume produced across different batches. 
The regression line helps visualize the overall trend, indicating whether higher bitterness levels correlate with higher sales.
""")

df = pd.DataFrame(filtered_data)
filtered_data['Sales_Volume_Ratio'] = filtered_data['Total_Sales']/filtered_data['Volume_Produced']

x_min = filtered_data['Bitterness'].min()
x_max = filtered_data['Bitterness'].max()
y_min = filtered_data['Sales_Volume_Ratio'].min()
y_max = filtered_data['Sales_Volume_Ratio'].max()

scatter = alt.Chart(filtered_data).mark_circle(size=60, color="#FF5D50").encode(
    x=alt.X('Bitterness', scale=alt.Scale(domain=(x_min, x_max)), axis=alt.Axis(title='Bitterness')),
    y=alt.Y('Sales_Volume_Ratio', scale=alt.Scale(domain=(y_min, y_max)), axis=alt.Axis(title='Sales to Volume Ratio')),
    tooltip=['Bitterness', 'Sales_Volume_Ratio'] 
)

regression_line = alt.Chart(filtered_data).transform_regression(
    'Bitterness', 'Sales_Volume_Ratio', method='poly', order=6
).mark_line(color='#FFC46F').encode(
    x='Bitterness',
    y='Sales_Volume_Ratio'
)

chart = scatter + regression_line

tab1.altair_chart(chart, use_container_width=True)

tab1.subheader('Total Sales of Different SKUs')
tab1.caption("""
This bar chart shows the total sales for different SKU types. Each bar represents the aggregate sales for a specific SKU, helping to visualize which SKU types correlate with higher sales.
""")

bar_chart = alt.Chart(filtered_data).mark_bar(color="#FF5D50").encode(
    x=alt.X('SKU:N', title='SKU'),
    y=alt.Y('sum(Total_Sales):Q', title='Total Sales'),
    tooltip=[alt.Tooltip('SKU:N'), alt.Tooltip('sum(Total_Sales):Q')]
)

tab1.altair_chart(bar_chart, use_container_width=True)


tab1.subheader('Sales/Volume of Different SKUs')
tab1.caption("""
This bar chart shows the total sales to volume produced ratio for different SKU types. Each bar represents the aggregate sales for a specific SKU, helping to visualize which SKU types correlate with higher sales.
""")

df = pd.DataFrame(filtered_data)
df['Sales_Volume_Ratio'] = df['Total_Sales']/df['Volume_Produced']

bar_chart = alt.Chart(df).mark_bar(color="#FF5D50", stroke="#FF5D50").encode(
    x=alt.X('SKU', title='SKU'),
    y=alt.Y('Sales_Volume_Ratio', title='Sales to Volume Ratio'),
    tooltip=[alt.Tooltip('SKU'), alt.Tooltip('Sales_Volume_Ratio', title='Sales/Volume Ratio')]
)

tab1.altair_chart(bar_chart, use_container_width=True)


tab1.subheader('Sales vs. Alcohol Content')
tab1.caption("""
This scatter plot shows the relationship between alcohol content and total sales across different batches. 
The regression line helps visualize the overall trend, indicating whether higher alcohol content correlates with higher sales.
""")

x_min = filtered_data['Alcohol_Content'].min()
x_max = filtered_data['Alcohol_Content'].max()
y_min = filtered_data['Total_Sales'].min()
y_max = filtered_data['Total_Sales'].max()

scatter = alt.Chart(filtered_data).mark_circle(size=60, color="#FF5D50").encode(
    x=alt.X('Alcohol_Content', scale=alt.Scale(domain=(x_min, x_max)), axis=alt.Axis(title='Alcohol Content (%)')),
    y=alt.Y('Total_Sales', scale=alt.Scale(domain=(y_min, y_max)), axis=alt.Axis(title='Total Sales')),
    tooltip=['Alcohol_Content', 'Total_Sales'] 
)

regression_line = alt.Chart(filtered_data).transform_regression(
    'Alcohol_Content', 'Total_Sales', method='poly', order=3
).mark_line(color='#FFC46F').encode(
    x='Alcohol_Content',
    y='Total_Sales'
)

chart = scatter + regression_line

tab1.altair_chart(chart, use_container_width=True)



tab1.subheader('Fermentation Time Distribution of Filtered Data')
tab1.caption("""
This histogram shows the distribution of fermentation times for the filtered dataset. 
It highlights the most common durations that brewing processes take under the selected conditions.
""")

bar_chart = alt.Chart(filtered_data).mark_bar(color="#FF5D50").encode(
    x=alt.X('Fermentation_Time:N', title='Fermentation Time (Days)'),
    y=alt.Y('count(Fermentation_Time):Q', title='Frequency'),
    tooltip=[alt.Tooltip('Fermentation_Time:N'), alt.Tooltip('sum(Fermentation_Time):Q')]
)

tab1.altair_chart(bar_chart, use_container_width=True)



tab1.subheader('Relationship between Fermentation Time and Alcohol Content')
tab1.caption("""
This scatter plot with regression line illustrates any potential correlation between the duration of fermentation and the alcohol content in the beer.
""")

x_min = filtered_data['Fermentation_Time'].min()
x_max = filtered_data['Fermentation_Time'].max()
y_min = filtered_data['Alcohol_Content'].min()
y_max = filtered_data['Alcohol_Content'].max()

scatter = alt.Chart(filtered_data).mark_circle(size=60, color="#FF5D50").encode(
    x=alt.X('Fermentation_Time', scale=alt.Scale(domain=(x_min, x_max)), axis=alt.Axis(title='Fermentation Time (Days)')),
    y=alt.Y('Alcohol_Content', scale=alt.Scale(domain=(y_min, y_max)), axis=alt.Axis(title='Alcohol Content (%)')),
    tooltip=['Fermentation_Time', 'Alcohol_Content'] 
)

regression_line = alt.Chart(filtered_data).transform_regression(
    'Fermentation_Time', 'Alcohol_Content', method='poly', order=3
).mark_line(color='#FFC46F').encode(
    x='Fermentation_Time',
    y='Alcohol_Content'
)

chart = scatter + regression_line

tab1.altair_chart(chart, use_container_width=True)
