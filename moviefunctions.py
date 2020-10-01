import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')
pd.options.display.float_format = "{:,.2f}".format
import warnings
warnings.filterwarnings('ignore')
import matplotlib.ticker as mtick
import moviefunctions


# imdb_title_basics cleaning
def imdb_clean():
    imdb_title_basics = pd.read_csv('./data/imdb.title.basics.csv')
    imdb_title_basics.drop(columns = {'runtime_minutes','start_year'}, inplace = True)
    imdb_title_basics = imdb_title_basics.loc[imdb_title_basics.genres.isna() == False] # This line removes rows where genre is missing
    imdb_title_basics.rename({'tconst': 'movie_id'}, axis = 1, inplace=True)
    return imdb_title_basics


def tn_clean():
    tn_movie_budgets = pd.read_csv('./data/tn.movie_budgets.csv')
    tn_movie_budgets = tn_movie_budgets.drop(columns={'id'})
    tn_movie_budgets.rename({'movie': 'primary_title'}, axis = 1, inplace=True)

### cleaning columns of $ and , and makes them floats
    tn_movie_budgets.production_budget = clean_columns(tn_movie_budgets.production_budget)
    tn_movie_budgets.domestic_gross = clean_columns(tn_movie_budgets.domestic_gross)
    tn_movie_budgets.worldwide_gross = clean_columns(tn_movie_budgets.worldwide_gross)
    tn_movie_budgets.release_date = tn_movie_budgets.release_date.apply(lambda x: int(x[-4:]))
###
    tn_movie_budgets['budget_gross_ratio'] = tn_movie_budgets.worldwide_gross / tn_movie_budgets.production_budget
    tn_movie_budgets = tn_movie_budgets.loc[tn_movie_budgets.domestic_gross > 0] # Drops rows with missing gross data
    return tn_movie_budgets


# column cleaner function
def clean_columns(series):
    return series.apply(lambda x: float(x.replace('$', '').replace(',', '')))

### Table Merger
def mergetables(tn, imdb):
    merge= tn.merge(imdb, on= 'primary_title')
    merge.drop_duplicates(subset='movie_id', keep='first', inplace=True)
    merge = merge.drop(merge[merge.primary_title.duplicated()&merge.production_budget.duplicated()].index)
    merge['net_profit'] = merge.worldwide_gross-merge.production_budget
    merge = merge.drop(columns={'original_title','movie_id'})   
    return merge

def make_bgr_hist_plot(data):
    bgr = data.budget_gross_ratio
    fig, ax = plt.subplots(figsize=(14,6))
    ax.set_title('Distribution of Movie Profitability', fontsize=30)
    ax.set_xlabel('<-Low Profit    Ratio of Revenue to Budget    High Profit->',fontsize = 24)
    ax.set_ylabel('Number of Movies',fontsize=24)
    ax.tick_params(labelsize = 14)
    ax.hist(bgr, range=(1,15), bins = 25);
    ax.plot([2,2],[0,300], color = 'r')
    fig.savefig('./images/hist-bgr.png',bbox_inches='tight')
    return


def make_bgr_boxplot(data, indices):
    fig, ax = plt.subplots(figsize = (14,6))
    bgrdata = [data.loc[data.genres==x].budget_gross_ratio for x in indices]
    ax.set_title('Profitability By Genre', fontsize=30)
    ax.set_ylabel('Ratio of Revenue to Budget', fontsize = 24)
    ax.set_xlabel('Genre', fontsize = 24)
    ax.set_xticklabels(indices, rotation=45, horizontalalignment='right', fontsize=16)
    ax.boxplot(bgrdata, showfliers=False);
    ax.plot([.5,16.5],[2,2], color = 'r')
    fig.savefig('./images/boxplot-bgr.png',bbox_inches='tight')
    return


def make_gross_boxplot(data, indices):
    fig, ax = plt.subplots(figsize = (14,6))
    grossdata = [data.loc[data.genres==x].net_profit for x in indices]
    ax.set_title('Net Profit By Genre', fontsize=30)
    ax.set_ylabel('Net Profit', fontsize = 24)
    ax.set_xlabel('Genre', fontsize = 24)
    ax.set_xticklabels(indices, rotation=45, horizontalalignment='right', fontsize=16)

    ### Dollar ticks
    fmt = '${x:,.0f}'
    tick = mtick.StrMethodFormatter(fmt)
    ax.yaxis.set_major_formatter(tick) 
    ax.tick_params(labelsize='large')
    ###

    ax.boxplot(grossdata, showfliers=False);
    ax.plot([0.5,16.5],[0,0], color = 'r')
    fig.savefig('./images/boxplot-netprofit.png', bbox_inches='tight')
    return


