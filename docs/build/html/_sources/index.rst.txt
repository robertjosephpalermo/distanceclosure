Distance Closure: The Distance Backbone of Complex Networks
============================================================

Description
-------------

This package implements methods for the calculation of the `distance closure` of complex networks, including its `metric` and `ultrametric` backbone.

The distance backbone is a principled graph reduction technique. It is a small subgraph sufficicent to compute all shortest paths lengths.
This method is suited for both undirected and directed weighted graphs. If the edge weights represent a notion of distance (dissimilarity), where smaller values represent stronger interactions, follow the guide below. If the edge weights represent a notion of proximity (similarity), where larger values represent stronger interactions, one should transform to an isomorphic distance measure using the `prox2dist` function in the `distanceclosure.utils` script.


Quick Install
--------------
.. code-block:: bash

    $pip install distanceclosure


Core Functionality
---------------------------------------
A comprehensive overview can be found in the :doc:`reference/index` page.

- :func:`distance_closure <distanceclosure.closure.distance_closure>`: Computes transitive closure on a weighted graph.
- :func:`metric_backbone <distanceclosure.backbone.metric_backbone>`: Computes the shortest path metric backbone on a weighted graph.
- :func:`ultrametric_backbone <distanceclosure.backbone.ultrametric_backbone>`: Computes the shortest path ultrametric backbone on a weighted graph.
- :func:`prox2dist <distanceclosure.utils.prox2dist>`: Transforms a non-negative [0,1] proximity to distance in the [0,inf] interval.



Simple Usage
-------------
Instantciate a weighted graph:

.. code-block:: python

    import networkx as nx
    import distanceclosure as dc

    edge_list = {
        ('s', 'a'): 8, 
        ('s', 'c'): 6, 
        ('s', 'd'): 5,
        
        ('a', 'd'): 2, 
        ('a', 'e'): 1,
        
        ('b', 'e'): 6,
        
        ('c', 'd'): 3, 
        ('c', 'f'): 9,
        
        ('d', 'f'): 4,
        
        ('e', 'g'): 4,
        
        ('f', 'g'): 0
    }
    G = nx.from_edgelist(edge_list)

    # Assign edge distances 
    nx.set_edge_attributes(G, name='distance', values=edge_list)


Compute the metric closure (may be slow for large graphs):

.. code-block:: python

    closure_metric = dc.distance_closure(G, kind='metric', weight='distance')

    # Access the metric distance and backbone membership
    closure_metric['s']['c']
    > {'distance': 6, 'metric_distance': 6, 'is_metric': True}

    closure_metric.number_of_edges()
    > 22


Compute the metric backbone:

.. code-block:: python

    backbone_metric = dc.distance_closure(G, kind='metric', weight='distance', only_backbone=True)

    backbone_metric.number_of_edges()
    > 11


Recent Publications Using These Methods
---------------------------------------

- :cite:`brattig2024conserved` Brattig-Correia, Rion and Almeida, Joana M and Wyrwoll, Margot Julia and Julca, Irene and Sobral, Daniel and Misra, Chandra Shekhar and Di Persio, Sara and Guilgur, Leonardo Gaston and Schuppe, Hans-Christian and Silva, Neide and others. `The conserved genetic program of male germ cells uncovers ancient regulators of human spermatogenesis`__ *In Elife, 13:RP95774, 2024.* doi:10.7554/eLife.95774

__ https://doi.org/10.7554/eLife.95774



- :cite:`brattig2023contact` Brattig Correia, Rion and Barrat, Alain and Rocha, Luis M `Contact networks have small metric backbones that maintain community structure and are primary transmission subgraphs`__ *In PLOS Computational Biology, 19(2):e1010854, 2023.* doi:10.1371/journal.pcbi.1010854

__ https://doi.org/10.1371/journal.pcbi.1010854


- :cite:`Correia:2016` Rion Brattig Correia, Lang Li, and Luis M. Rocha. `Monitoring potential drug interactions and reactions via network analysis of instagram user timelines`__ *In Pacific Symposium on Biocomputing, volume 21, pages 492–503. 2016.* doi:10.1142/9789814749411_0045
    
__ http://www.informatics.indiana.edu/rocha/publications/PSB2016.php


Formal definition
------------------

For the formal definition of the distance backbone, please refer to

- :cite:`Simas:2021` Tiago Simas, Rion Brattig Correia, and Luis M. Rocha. `The distance backbone of complex networks`__ *In Journal of Complex Networks, 9:cnab021, 2021.* doi:10.1093/comnet/cnab021

__ http://doi.org/10.1093/comnet/cnab021

- :cite:`Simas:2015` Tiago Simas and Luis M. Rocha. `Distance closures on complex networks`__ *In Network Science, 3:227–268, 6 2015.* doi:10.1017/nws.2015.11

__ http://doi.org/10.1017/nws.2015.11

Additional papers :cite:`Rocha:2002,Rocha:2005,Simas:2012,Ciampaglia:2015,Simas:2015,Correia:2016,Simas:2021,brattig2024conserved,brattig2023contact` can be found in the :doc:`bibliography` page.

..
    Citation
    ---------

    .. code-block:: bib
        @article{Simas:2021,
            author = {Tiago Simas and Rion Brattig Correia and Luis M. Rocha},
            doi = {10.1093/comnet/cnab021},
            issue = {6},
            journal = {Journal of Complex Networks},
            pages = {cnab021},
            title = {The distance backbone of complex networks},
            volume = {9},
            year = {2021}
        }


.. toctree::
    :maxdepth: 3
    :hidden:

    install
    tutorial
    reference/index
    development
    bibliography

..
    Indices and tables
    ===================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

