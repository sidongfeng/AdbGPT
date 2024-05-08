def sortchildrenby_viewhierarchy(view, attr="bounds"):
    if attr == 'bounds':
        bounds = [(ele.uiobject.bounding_box.x1, ele.uiobject.bounding_box.y1, 
                    ele.uiobject.bounding_box.x2, ele.uiobject.bounding_box.y2)  
                    for ele in view]
        sorted_bound_index = [bounds.index(i) for i in sorted(bounds, key = lambda x: (x[1], x[0]))]
    
        sort_children = [view[i] for i in sorted_bound_index]
        view[:] = sort_children