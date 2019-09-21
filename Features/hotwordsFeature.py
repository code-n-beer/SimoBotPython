# coding=utf-8

import pandas as pd
import sqlite3
import numpy as np
import re
#conn = sqlite3.connect("/simojs-data/simojs-logs.sqlite")
#conn = sqlite3.connect("./Resources/simojs-logs-lemmatized.sqlite")
conn = sqlite3.connect("/simojs-data/simojs-logs-lemmatized.sqlite")

class hotwordsFeature:
    def __init__(self):
        self.cmdpairs = {
                u"!trend" : self.execute,
                }

    def execute(self, queue, nick, msg, channel):
        try:
            from_ago = msg.split()[1]
            time_type = msg.split()[2]
            periods = msg.split()[3]

            words = process(time_type, int(periods), int(from_ago))
            print('words', words)
            words = ', '.join(words)
            print('words', words)
            queue.put((words, channel))
        except Exception as e:
            queue.put(('failed', channel))
            queue.put((str(e), channel))


def get_sorted_counts(tags):
    unique, counts = np.unique(tags, return_counts=True)
    sort_ind = np.argsort(-counts)
    return unique[sort_ind], counts[sort_ind]

#regex = re.compile('[^a-zA-ZäÄöÖåÅ:)(!<>\\/]') # with all basic special chars
regex = re.compile(u'[^a-zA-ZäÄöÖåÅ]')
def count_words(messages):
    lines = [line.split(' ') for line in messages]
    lines = np.array(filter(lambda x: len(x) >= 2, [regex.sub('', word).lower() for x in lines for word in x]))
    uniqs, counts = get_sorted_counts(lines)
    #print('uniqs shape', uniqs.shape)
    #print('uniqs', uniqs[:10])
    #print('counts', counts[:10])
    #print('line shape', lines.shape)
    #print('line first 10', lines[:10])
    return uniqs, counts

def get_common_uniques(uniqs):
    all_uniqs = [y for x in uniqs for y in x]
    print('shape 1', len(all_uniqs))

    all_uniqs, counts = np.unique(all_uniqs, return_counts=True)
    print('shape 2', all_uniqs.shape)
    print('all uniqs 0', all_uniqs[0])

    return all_uniqs, counts

# Build vector that has zeros for elements not in this set
def build_vec(all_tags, tags, counts):
    vec = np.zeros(len(all_tags))
    for idx_all, tag in enumerate(all_tags):
        idxs = np.where(tags == tag)
        if len(idxs) >= 1 and len(idxs[0]) > 0:
            idx = idxs[0][0]
            vec[idx_all] = counts[idx]
    return vec

def process(time_type, periods, from_ago):
    print('processing hot words in {} periods since {} {} ago'.format(periods, from_ago, time_type))

    df = pd.read_sql_query("select * from logs;", conn)
    #df['timestamp'] = pd.to_datetime(df.timestamp, utc=True)
    df['timestamp'] = pd.to_datetime(df.timestamp)
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Europe/Helsinki')

    print(df.iloc[0])
    #print(df.timestamp)


    parameter = {time_type: from_ago}
    #parameter = {'seconds': from_ago}
    #dates = pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(seconds=from_ago), end=pd.Timestamp.now(), periods=periods+1, tz='Europe/Helsinki')
    dates = pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(**parameter), end=pd.Timestamp.now(), periods=periods+1, tz='Europe/Helsinki')
    print('len', len(dates))

    #words = []
    uniqs_all = []
    counts_all = [] 
    count_in_range = 0
    for idx in xrange(0, len(dates)-1):
        date_lower = dates[idx]
        date_higher = dates[idx + 1]
        df_range = df[(df.timestamp > date_lower) & (df.timestamp < date_higher)]
        #df_range = df[df.timestamp > dates[idx] & df.timestamp < dates[idx+1]]
        print('lower {} higher {}'.format(date_lower, date_higher))
        print('date', len(df_range))
        count_in_range += len(df_range)

        messages = df_range.lemmatized_message.values
        #print('messages len', messages.shape)
        #print('messages flattened', messages.flatten().shape)

        uniqs, counts = count_words(messages)
        uniqs_all.append(uniqs)
        counts_all.append(counts)


    if count_in_range == 0:
        return []

    print('calculate total occurences of words')
    total_uniqs, total_counts = count_words(df.lemmatized_message.values)
    df_totals = pd.DataFrame(total_counts, index=total_uniqs, columns=['count'])
    print('totals', df_totals)

    common_uniqs, common_counts = get_common_uniques(uniqs_all)
    print('common uniqs shape', common_uniqs.shape)
    print('common uniqs 0', common_uniqs[:10])

    vecs = []
    for idx in xrange(0, len(dates)-1):
        print('build vec', idx)
        vec = build_vec(common_uniqs, uniqs_all[idx], counts_all[idx])
        #print(vec)
        vec = tuple(vec)
        #print(vec)
        vecs.append(vec)

    vecs = np.array(vecs)

    columns = common_uniqs
    #print('vecs', vecs[0])
    #print('columns', columns)
    #print('len vecs', len(vecs))
    #print('len vecs 0 ', len(vecs[0]))
    #print('len columns', len(columns))
    df_counts = pd.DataFrame.from_records(vecs, columns=columns)
    df_counts.loc['mean'] = df_counts.mean()
    df_counts.loc['std'] = df_counts.std()
    #df_counts['mean'] = df_counts.mean()
    #df_counts['std'] = df_counts.std()

    df_counts_zscore = (df_counts - df_counts.loc['mean']) / df_counts.loc['std']

    last_idx = len(df_counts_zscore) - 1 - 2
    row = df_counts_zscore.loc[last_idx]
    #row = row[row.index != 'mean']
    #row = row[row.index != 'std']
    #row.dropna(inplace=True)

    df = pd.DataFrame({'word': common_uniqs, 'zscore': row, 'uniq_days_mentioned': common_counts}).join(df_totals)
    df_sorted = df.sort_values(by=['zscore', 'uniq_days_mentioned', 'count'], ascending=[False, False, False])

    top_words = df_sorted[:5].word.values
    return top_words


#print(process('days', 10, 100))