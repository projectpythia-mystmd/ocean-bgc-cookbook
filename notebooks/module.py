import numpy as np

def adjust_pop_grid(tlon,tlat,field):
    """
    Adjusts the grid of longitude and latitude values, along with the corresponding field data.

    Parameters
    ----------
    tlon : numpy.ndarray
        2D array of longitude values.
    tlat : numpy.ndarray
        2D array of latitude values.
    field : numpy.ma.MaskedArray
        2D array of field data (e.g., temperature, salinity) corresponding to the tlon and tlat arrays.

    Returns
    -------
    lon : numpy.ndarray
        Adjusted 2D array of longitude values.
    lat : numpy.ndarray
        Adjusted 2D array of latitude values.
    field : numpy.ma.MaskedArray
        Adjusted 2D array of field data.

    Example
    -------
    >>> lon, lat, field = adjust_pop_grid(tlon, tlat, field)
    """
    nj = tlon.shape[0]
    ni = tlon.shape[1]
    xL = int(ni/2 - 1)
    xR = int(xL + ni)

    tlon = np.where(np.greater_equal(tlon,min(tlon[:,0])),tlon-360.,tlon)
    lon  = np.concatenate((tlon,tlon+360.),1)
    lon = lon[:,xL:xR]

    if ni == 320:
        lon[367:-3,0] = lon[367:-3,0]+360.
    lon = lon - 360.
    lon = np.hstack((lon,lon[:,0:1]+360.))
    if ni == 320:
        lon[367:,-1] = lon[367:,-1] - 360.

    # Trick cartopy into doing the right thing:
    # it gets confused when the cyclic coords are identical
    lon[:,0] = lon[:,0]-1e-8
    
    # Periodicity
    lat  = np.concatenate((tlat,tlat),1)
    lat = lat[:,xL:xR]
    lat = np.hstack((lat,lat[:,0:1]))

    field = np.ma.concatenate((field,field),1)
    field = field[:,xL:xR]
    field = np.ma.hstack((field,field[:,0:1]))
    return lon,lat,field
