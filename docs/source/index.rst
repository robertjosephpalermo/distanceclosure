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
--------------
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
        
        ('f', 'g'): 0,
    }
    G = nx.from_edgelist(edge_list)

    # Assign edge distances 
    nx.set_edge_attributes(G, name='distance', values=edge_list)


Compute the metric closure (may be slow for large graphs):

.. code-block:: python

    closure = dc.distance_closure(G, kind='metric', weight='distance')

    # Access the metric distance and backbone membership
    closure['s']['c']
    > {'distance': 6, 'metric_distance': 6, 'is_metric': True}

    closure.number_of_edges()
    > 22


Compute the metric backbone:

.. code-block:: python

    backbone = dc.distance_closure(G, kind='metric', weight='distance', only_backbone=True)

    backbone.number_of_edges()
    > 11


Recent Publications Using These Methods
------------------
NEEDS UPDATE

- :cite:`Correia:2022:meionav` Rion Brattig Correia, J.M. Almeida, M. Wyrwoll, I. Julca, D. Sobral, C.S. Misra, L.G. Guilgur, H. Schuppe, N. Silva, P. Prudêncio, A. Nóvoa, A.S. Leocádio, J. Bom, M. Mallo, S. Kliesch, M. Mutwil, Luis M. Rocha, F. Tüttelmann, J.D. Becker, and Paulo Navarro-Costa. `An old transcriptional program in male germ cells uncovers new causes of human infertility`__. **Under review**, 2022. doi:10.1101/2022.03.02.482557v2.

__ http://doi.org/10.1101/2022.03.02.482557v2

- :cite:`Correia:2022:contact` Rion Brattig Correia, Alain Barrat, and Luis M. Rocha. `The metric backbone preserves community structure and is a primary transmission subgraph in contact networks`__. **Under review**, 2022. doi:10.1101/2022.02.02.478784

__ http://doi.org/10.1101/2022.02.02.478784.

- :cite:`Correia:2016` Rion Brattig Correia, Lang Li, and Luis M. Rocha. `Monitoring potential drug interactions and reactions via network analysis of instagram user timelines`__. In *Pacific Symposium on Biocomputing*, volume 21, pages 492–503. 2016. doi:10.1142/9789814749411_0045.
    
__ http://www.informatics.indiana.edu/rocha/publications/PSB2016.php


Formal definition
------------------

For the formal definition of the distance backbone, please refer to

- :cite:`Simas:2021` Tiago Simas, Rion Brattig Correia, and Luis M. Rocha. `The distance backbone of complex networks`__. *Journal of Complex Networks*, 9:cnab021, 2021. doi:10.1093/comnet/cnab021.

__ http://doi.org/10.1093/comnet/cnab021

- :cite:`Simas:2015` Tiago Simas and Luis M. Rocha. `Distance closures on complex networks`__. *Network Science*, 3:227–268, 6 2015. doi:10.1017/nws.2015.11.

__ http://doi.org/10.1017/nws.2015.11

Additional papers :cite:`Rocha:2002,Rocha:2005,Simas:2012,Ciampaglia:2015,Simas:2015,Correia:2016,Simas:2021, Correia:2022:contact,Correia:2022:meionav` can be found in the :doc:`bibliography` page.

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

