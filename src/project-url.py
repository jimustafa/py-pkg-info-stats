# %% [markdown]
"""
# <center>Python PKG-INFO Stats</center>
## <center>Project-URL</center>
"""


# %%
# %matplotlib widget
import os
import pathlib
import urllib

import pandas as pd


df = pd.read_csv(pathlib.Path().resolve() / 'table.csv')

query_string = os.environ.get('QUERY_STRING', '')
query_parameters = urllib.parse.parse_qs(query_string)

initial_item = query_parameters.get('item', ['homepage'])[0]

parameters = {
    'item': initial_item,
    'normalization': 'abs',
    'yscale': 'linear',
    'selected_labels': list(df[df['item']==initial_item]['label'].value_counts().index),
}


# %%
# %matplotlib widget
import ipyvuetify as v
import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import traitlets


output = widgets.Output()


class Figure():
    def __init__(self):
        (fig, ax) = plt.subplots()

        fig.canvas.header_visible = False
        fig.canvas.toolbar_visible = True
        fig.canvas.toolbar_position = 'right'

        self.fig = fig
        self.ax = ax

        self.update()

        self.fig.tight_layout()

    @property
    def canvas(self):
        return self.fig.canvas

    @output.capture()
    def update(self):
        self.plot()

        if parameters['normalization'] == 'abs' and parameters['yscale'] == 'log':
            self.ax.set_yscale('symlog', subs=[2, 3, 4, 5, 6, 7, 8, 9])
        else:
            self.ax.set_yscale(parameters['yscale'])

        if parameters['normalization'] == 'abs':
            self.ax.set_ylabel('Count')
            self.ax.set_ylim(bottom=0)
            self.ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.0f'))
        if parameters['normalization'] == 'rel':
            self.ax.set_ylabel('Fraction')
            self.ax.set_ylim([1e-3, 1e0])
            self.ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%g'))

        self.ax.set_axisbelow(True)
        self.ax.grid(True, which='both')

        self.fig.canvas.draw_idle()

    def plot(self):
        df_tmp = df[df['item']==parameters['item']]['label']
        categories = df_tmp.value_counts().index
        counts = df_tmp.value_counts().values
        if parameters['normalization'] == 'rel':
            values = counts/counts.sum()
        if parameters['normalization'] == 'abs':
            values = counts

        self.ax.clear()
        self.ax.bar(categories, values)
        self.ax.set_xticks(self.ax.get_xticks(), categories, rotation=45, ha='right')


class MyDataTable(v.VuetifyTemplate):
    headers = traitlets.List([]).tag(sync=True, allow_null=True)
    items = traitlets.List([]).tag(sync=True, allow_null=True)

    @traitlets.default('template')
    def _template(self):
        return '''
          <v-data-table
            :headers="headers"
            :items="items"
            :items-per-page="20"
            :footer-props="{
                'items-per-page-options': [10, 20, 50, 100, -1]
            }"
            style="width: 100%"
          >
            <template v-slot:item.package="{ item }">
              <a :href="`https://pypi.org/project/${item.package}`" target="_blank">{{ item.package }}</a>
            </template>
          </v-data-table>
        '''


class Table(MyDataTable):
    def __init__(self):
        super().__init__(
            headers=[
                {'text': 'Package', 'value': 'package'},
                {'text': 'SourceRank', 'value': 'rank'},
                {'text': 'Item', 'value': 'item'},
                {'text': 'Label', 'value': 'label'},
            ],
        )

        self.update()

    def update(self):
        df_tmp = df[(df['item']==parameters['item']) & (df['label'].isin(parameters['selected_labels']))]

        self.items = [
            {
                'package': record['package'],
                'rank': record['rank'],
                'item': record['item'],
                'label': record['label'],
            }
            for (_, record) in df_tmp.iterrows()
        ]


plt.ioff()

figure = Figure()
table = Table()


item = v.Select(
    label='Item',
    items=[
        'homepage',
        'documentation',
        'issues',
        'changelog',
        'funding',
        'github',
        'gitlab',
        'bitbucket',
        'other',
        ],
    value=parameters['item'],
)

normalization = v.RadioGroup(
    v_model=parameters['normalization'],
    v_slots=[{
        'name': 'label',
        'children': v.Html(tag='div', children=['Normalization:']),
    }],
    row=True,
    children=[
        v.Radio(label='abs', value='abs'),
        v.Radio(label='rel', value='rel'),
    ]
)

yscale = v.RadioGroup(
    v_model=parameters['yscale'],
    v_slots=[{
        'name': 'label',
        'children': v.Html(tag='div', children=['Scale:']),
    }],
    row=True,
    children=[
        v.Radio(label='linear', value='linear'),
        v.Radio(label='log', value='log'),
    ]
)

label_selector = v.Select(
    label='Labels',
    multiple=True,
    chips=True,
    items=list(df[df['item']==parameters['item']]['label'].value_counts().index),
    value=parameters['selected_labels']
)


def update_item(widget, event, data):
    parameters.update({'item': data})
    label_selector.items = list(df[df['item']==parameters['item']]['label'].value_counts().index)
    label_selector.value = list(df[df['item']==parameters['item']]['label'].value_counts().index)
    parameters.update({'selected_labels': list(df[df['item']==parameters['item']]['label'].value_counts().index)})
    figure.update()
    table.update()


def update_yscale(widget, event, data):
    parameters.update({'yscale': data})
    figure.update()


def update_normalization(widget, event, data):
    parameters.update({'normalization': data})
    figure.update()


def update_label_selector(widget, event, data):
    parameters.update({'selected_labels': data})
    table.update()


item.on_event('change', update_item)
normalization.on_event('change', update_normalization)
yscale.on_event('change', update_yscale)
label_selector.on_event('change', update_label_selector)


v.Container(fluid=True, children=[
    v.Row(children=[
        v.Col(cols=12, md=6, children=[
            v.Card(
                class_='mb-4',
                outlined=True,
                children=[
                    v.CardTitle(children=['Parameters']),
                    v.CardText(children=[
                        item,
                        normalization,
                        yscale,
                    ]),
            ]),
            v.Card(
                class_='mb-4',
                outlined=True,
                children=[
                    v.CardTitle(children=['Table']),
                    v.CardText(children=[
                        label_selector,
                        table,
                    ]),
            ]),
        ]),
        v.Col(cols=12, md=6, children=[
            v.Card(
                class_='mb-4',
                outlined=True,
                children=[
                    v.CardTitle(children=['Figure']),
                    v.CardText(children=[
                        figure.canvas,
                    ]),
            ]),
        ]),
    ]),
    v.Row(children=[
        v.Col(cols=12, md=12, children=[
            output
        ]),
    ]),
])
