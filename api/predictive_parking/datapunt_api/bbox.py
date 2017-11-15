"""
Bounding box methods usefull for Amsterdam.
"""

# Default amstermdam bbox lon, lat, lon, lat
# square around Amsterdam.
BBOX = [52.03560, 4.58565,
        52.48769, 5.31360]


def determine_bbox(request):
    """
    Create a bounding box if it is given with the request.
    """

    err = "invalid bbox given"

    if 'bbox' not in request.query_params:
        # set default value
        return BBOX, None

    bboxp = request.query_params['bbox']
    bbox, err = valid_bbox(bboxp)

    if err:
        return None, err

    return bbox, err


def valid_bbox(bboxp):
    """
    Check if bbox is a valid bounding box
    """
    bbox = bboxp.split(',')
    err = None

    # check if we got 4 parametes
    if not len(bbox) == 4:
        return [], "wrong numer of arguments (lon, lat, lon, lat)"

    # check if we got floats
    try:
        bbox = [float(f) for f in bbox]
    except ValueError:
        return [], "Did not recieve floats"

    # max bbox sizes from mapserver
    # RD  EXTENT      100000    450000   150000 500000
    # WGS             52.03560, 4.58565  52.48769, 5.31360
    lat_min = 52.03560
    lat_max = 52.48769
    lon_min = 4.58565
    lon_max = 5.31360

    # check if coorinates are withing amsterdam
    # lat1, lon1, lat2, lon2 = bbox

    # bbox given by leaflet
    lon1, lat1, lon2, lat2 = bbox

    if not lat_max >= lat1 >= lat_min:
        err = f"lat not within max bbox {lat_max} > {lat1} > {lat_min}"

    if not lat_max >= lat2 >= lat_min:
        err = f"lat not within max bbox {lat_max} > {lat2} > {lat_min}"

    if not lon_max >= lon2 >= lon_min:
        err = f"lon not within max bbox {lon_max} > {lon2} > {lon_min}"

    if not lon_max >= lon1 >= lon_min:
        err = f"lon not within max bbox {lon_max} > {lon1} > {lon_min}"

    # this is how the code expects the bbox
    bbox = [lat1, lon1, lat2, lon2]

    return bbox, err
