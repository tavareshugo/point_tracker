__author__ = "Pierre Barbier de Reuille <pbdr@uea.ac.uk>"
__docformat__ = "restructuredtext"
from PyQt4.QtCore import (QCoreApplication, QObject,  QSettings,  QVariant,  QRectF,
        SIGNAL,  Qt)
from PyQt4.QtGui import QColor, QFontMetricsF, QFont
from path import path
from math import floor, ceil

class Parameters(QObject):
    """
    Signal launched when parameters change:
        - pointParameterChange
        - oldPointParameterChange
        - arrowParameterChange
        - searchParameterChange
        - renderingChanged
        - recentProjectsChange
        - cellParameterChange
        - plottingParameterChange
    """
    def __init__(self):
        QObject.__init__(self)
        self.load()

    # Use thread or not to compute on the background
    use_thread = False

    def load(self):
        settings = QSettings()

        settings.beginGroup("GraphicParameters")
# First, parameters for normal points
        self._point_size = None
        _point_size, success = settings.value("PointSize").toDouble()
        if not success:
            _point_size = 5.0
        self.point_size = _point_size
        self._point_thickness = None
        _point_thickness, success = settings.value("PointThickness").toInt()
        if not success:
            _point_thickness = 0
        self.point_thickness = _point_thickness
        self._point_color = None
        _point_color = QColor(settings.value("PointColor"))
        if not _point_color.isValid():
            _point_color = QColor(Qt.red)
        self.point_color = _point_color
        _selected_point_color = QColor(settings.value("SelectedPointColor"))
        if not _selected_point_color.isValid():
            _selected_point_color = QColor(255, 128, 128, 255)
        self._selected_point_color = _selected_point_color
        _new_point_color = QColor(settings.value("NewPointColor"))
        if not _new_point_color.isValid():
            _new_point_color = QColor(Qt.blue)
        self._new_point_color = None
        self.new_point_color = _new_point_color

# Parameter for cells
        self._cell_size = None
        _cell_size, success = settings.value("CellSize").toDouble()
        if not success:
            _cell_size = 5.0
        self.cell_size = _cell_size
        self._cell_thickness = None
        _cell_thickness, success = settings.value("CellThickness").toInt()
        if not success:
            _cell_thickness = 1
        self.cell_thickness = _cell_thickness
        self._cell_color = None
        _cell_color = QColor(settings.value("CellColor"))
        if not _cell_color.isValid():
            _cell_color = QColor(Qt.darkCyan)
            _cell_color.setAlphaF(0.5)
        self.cell_color = _cell_color

        self._selected_cell_color = None
        _selected_cell_color = QColor(settings.value("SelectedCellColor"))
        if not _selected_cell_color.isValid():
            _selected_cell_color = QColor(Qt.yellow)
            _selected_cell_color.setAlphaF(0.5)
        self.selected_cell_color = _selected_cell_color

        self._division_wall_color = None
        _division_wall_color = QColor(settings.value("DivisionWallColor"))
        if not _division_wall_color.isValid():
            _division_wall_color = QColor(255,85,0)
            _division_wall_color.setAlphaF(0.8)
        self.division_wall_color = _division_wall_color

# Then, parameters for old points
        self._old_point_size, success = settings.value("OldPointSize").toDouble()
        if not success:
            self._old_point_size = 5.0
        self._old_point_thickness, success = settings.value("OldPointThickness").toInt()
        if not success:
                self._old_point_thickness = 0
        self._old_point_color = None
        self._old_point_color = QColor(settings.value("OldPointColor"))
        if not self._old_point_color.isValid():
            self._old_point_color = QColor(Qt.yellow)
        self._old_point_matching_color = QColor(settings.value("OldPointMatchingColor"))
        if not self._old_point_matching_color.isValid():
            self._old_point_matching_color = QColor(Qt.darkYellow)
        self._show_id = settings.value("ShowId", QVariant(False)).toBool()
# Parameters for arrow
        self._arrow_line_size, success = settings.value("ArrowLineSize").toDouble()
        if not success:
            self._arrow_line_size = 2
        self._arrow_head_size, success = settings.value("ArrowHeadSize").toDouble()
        if not success:
            self._arrow_head_size = .1
        self._arrow_color = QColor(settings.value("ArrowColor"))
        if not self._arrow_color.isValid():
            self._arrow_color = QColor(Qt.lightGray)
        self._draw_arrow = settings.value("DrawArrow", QVariant(True)).toBool()
        self._show_template = settings.value("ShowTemplate", QVariant(False)).toBool()
        self._template_color = QColor(settings.value("TemplateColor"))
        if not self._template_color.isValid():
            self._template_color = QColor(255,0,0,100)
        self._search_color = QColor(settings.value("SearchColor"))
        if not self._search_color.isValid():
            self._search_color = QColor(255,0,255,100)
        settings.endGroup()

# The search parameters
        settings.beginGroup("SearchParameters")
        self._template_size, success = settings.value("TemplateSize").toInt()
        if not success:
            self._template_size = 10
        s = self._template_size
        self.template_rect = QRectF(-s, -s, 2*s, 2*s)
        self._search_size, success = settings.value("SearchSize").toInt()
        if not success:
            self._search_size = 50
        s = self._search_size
        self.search_rect = QRectF(-s, -s, 2*s, 2*s)
        self._estimate = settings.value("Estimate", QVariant(True)).toBool()
        self._filter_size_ratio, success = settings.value("FilterSizeRatio").toDouble()
        if not success:
            self._filter_size_ratio = .5
        settings.endGroup()

        settings.beginGroup("GUI")
        self._show_vectors = settings.value("ShowVectors", QVariant(True)).toBool()
        self._link_views = settings.value("LinkViews", QVariant(True)).toBool()
        cache_size, success = settings.value("CacheSize").toInt()
        if not success:
            cache_size = 200
        self.cache_size = cache_size
        self._last_dir = path(settings.value("LastsDir", QVariant(".")).toString())
        self._use_OpenGL = settings.value("UseOpenGL", QVariant(True)).toBool()
        settings.beginGroup("RecentProjects")
        numproj, success = settings.value("NumberOfProjects").toInt()
        if not success:
            numproj = 0
        self._recent_projects = []
        if numproj > 0:
            for i in xrange(numproj):
                name = "Project%d" % i
                value = path(settings.value(name).toString())
                self._recent_projects.append(value)
        self._max_number_of_projects, success = settings.value("MaxNumberOfProjects").toInt()
        if not success:
            self._max_number_of_projects = 5
        settings.endGroup()
        settings.endGroup()

# The plotting parameters
        settings.beginGroup("PlottingParameters")
        settings.beginGroup("Ellipsis")
        self._ellipsis_scaling, success = settings.value("Scaling", QVariant(1.0)).toDouble()
        if not success:
            self._ellipsis_scaling = 1.0
        self._ellipsis_color = QColor(settings.value("Color"))
        if not self._ellipsis_color.isValid():
            self._ellipsis_color = QColor(0,0,0)
        self._ellipsis_thickness, success = settings.value("Thickness", QVariant(0)).toInt()
        if not success:
            self._ellipsis_thickness = 0
        self._ellipsis_min_anisotropy, success = settings.value("MinAnisotropy", QVariant(1e-3)).toDouble()
        if not success:
            self._ellipsis_min_anisotropy = 1e-3
        self._ellipsis_positive_color = QColor(settings.value("PositiveColor"))
        if not self._ellipsis_positive_color.isValid():
            self._ellipsis_positive_color = QColor(0,0,255)
        self._ellipsis_negative_color = QColor(settings.value("NegativeColor"))
        if not self._ellipsis_negative_color.isValid():
            self._ellipsis_negative_color = QColor(255,0,0)
        self._ellipsis_plot = settings.value("Plot").toBool()
        self._ellipsis_scale_axis = settings.value("ScaleAxis").toBool()
        settings.endGroup()
        settings.endGroup()
        self._point_editable = True
        self._point_selectable = True
        self._cell_editable = False

    def save(self):
        settings = QSettings()
        settings.beginGroup("GraphicParameters")
        settings.setValue("PointSize", QVariant(self._point_size))
        settings.setValue("PointColor", QVariant(self._point_color))
        settings.setValue("PointThickness", QVariant(self._point_thickness))
        settings.setValue("SelectedPointColor", QVariant(self._selected_point_color))
        settings.setValue("NewPointColor", QVariant(self._new_point_color))
        settings.setValue("CellSize", QVariant(self._cell_size))
        settings.setValue("CellColor", QVariant(self._cell_color))
        settings.setValue("CellThickness", QVariant(self._cell_thickness))
        settings.setValue("SelectedCellColor", QVariant(self._selected_cell_color))
        settings.setValue("DivisionWallColor", QVariant(self._division_wall_color))
        settings.setValue("OldPointSize", QVariant(self._old_point_size))
        settings.setValue("OldPointColor", QVariant(self._old_point_color))
        settings.setValue("OldPointMatchingColor", QVariant(self._old_point_matching_color))
        settings.setValue("ShowId", QVariant(self._show_id))
        settings.setValue("ArrowLineSize", QVariant(self._arrow_line_size))
        settings.setValue("ArrowHeadSize", QVariant(self._arrow_head_size))
        settings.setValue("ArrowColor", QVariant(self._arrow_color))
        settings.setValue("DrawArrow", QVariant(self._draw_arrow))
        settings.setValue("ShowTemplate", QVariant(self._show_template))
        settings.setValue("TemplateColor", QVariant(self._template_color))
        settings.setValue("SearchColor", QVariant(self._search_color))
        settings.endGroup()

        settings.beginGroup("SearchParameters")
        settings.setValue("TemplateSize", QVariant(self._template_size))
        settings.setValue("SearchSize", QVariant(self._search_size))
        settings.setValue("Estimate", QVariant(self._estimate))
        settings.setValue("FilterSizeRatio", QVariant(self._filter_size_ratio))
        settings.endGroup()

        settings.beginGroup("GUI")
        settings.setValue("UseOpenGL", QVariant(self._use_OpenGL))
        settings.setValue("ShowVectors", QVariant(self._show_vectors))
        settings.setValue("LinkViews", QVariant(self._link_views))
        settings.setValue("CacheSize", QVariant(self._cache_size))
        settings.setValue("LastsDir", QVariant(str(self._last_dir)))

        settings.beginGroup("RecentProjects")
        settings.setValue("MaxNumberOfProjects", QVariant(self._max_number_of_projects))
        settings.setValue("NumberOfProjects", QVariant(len(self._recent_projects)))
        for i,p in enumerate(self._recent_projects):
            name = "Project%d" % i
            settings.setValue(name, QVariant(str(p)))
        settings.endGroup()
        settings.endGroup()
# The plotting parameters
        settings.beginGroup("PlottingParameters")
        settings.beginGroup("Ellipsis")
        settings.setValue("Scaling", QVariant(self._ellipsis_scaling))
        settings.setValue("Color", QVariant(self._ellipsis_color))
        settings.setValue("Thickness", QVariant(self._ellipsis_thickness))
        settings.setValue("MinAnisotropy", QVariant(self._ellipsis_min_anisotropy))
        settings.setValue("PositiveColor", QVariant(self._ellipsis_positive_color))
        settings.setValue("NegativeColor", QVariant(self._ellipsis_negative_color))
        settings.setValue("Plot", QVariant(self._ellipsis_plot))
        settings.setValue("ScaleAxis", QVariant(self._ellipsis_scale_axis))
        settings.endGroup()
        settings.endGroup()

#{ On Screen Drawing

    def _get_point_size(self):
        """
        Size of a points on the scene
        """
        return self._point_size

    def _set_point_size(self, size):
        if size > 0 and size != self._point_size:
            self._point_size = size
            self._find_font()
            self.emit(SIGNAL("pointParameterChange"))

    point_size = property(_get_point_size, _set_point_size)

    def _get_point_color(self):
        """
        Color used to draw points
        """
        return self._point_color

    def _set_point_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._point_color:
            self._point_color = col
            self.point_hover_color = col.lighter(150)
            if self.point_hover_color == col:
                self.point_hover_color = col.lighter(50)
            self.emit(SIGNAL("pointParameterChange"))

    point_color = property(_get_point_color, _set_point_color)

    def _get_selected_point_color(self):
        """
        Set the color of a selected point
        """
        return self._selected_point_color

    def _set_selected_point_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._selected_point_color:
            self._selected_point_color = col
            self.emit(SIGNAL("pointParameterChange"))

    selected_point_color = property(_get_selected_point_color, _set_selected_point_color)

    def _get_new_point_color(self):
        """
        Set the color of a new point
        """
        return self._new_point_color

    def _set_new_point_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._new_point_color:
            self._new_point_color = col
            self.new_point_hover_color = col.lighter(150)
            if self.new_point_hover_color == col:
                self.new_point_hover_color = col.lighter(50)
            self.emit(SIGNAL("pointParameterChange"))

    new_point_color = property(_get_new_point_color, _set_new_point_color)

    def _get_cell_size(self):
        """
        Set the size of a cell graphic item
        """
        return self._cell_size

    def _set_cell_size(self, new_size):
        if new_size > 0 and new_size != self._cell_size:
            self._cell_size = new_size
            self.emit(SIGNAL("cellParameterChange"))

    cell_size = property(_get_cell_size, _set_cell_size)

    def _get_cell_thickness(self):
        """
        Set the thickness of the line used to draw the cell graphic item
        """
        return self._cell_thickness

    def _set_cell_thickness(self, th):
        thick = int(th)
        if thick >= 0 and thick != self._cell_thickness:
            self._cell_thickness = thick
            self.emit(SIGNAL("cellParameterChange"))

    cell_thickness = property(_get_cell_thickness, _set_cell_thickness)

    def _get_cell_color(self):
        """
        Set the color used to draw the cell
        """
        return self._cell_color

    def _set_cell_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._cell_color:
            self._cell_color = col
            self.cell_hover_color = col.lighter(150)
            if self.cell_hover_color == col:
                self.cell_hover_color = col.lighter(50)
            self.emit(SIGNAL("cellParameterChange"))

    cell_color = property(_get_cell_color, _set_cell_color)

    def _get_selected_cell_color(self):
        """
        Set the color used to draw the selected cell
        """
        return self._selected_cell_color

    def _set_selected_cell_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._selected_cell_color:
            self._selected_cell_color = col
            self.emit(SIGNAL("cellParameterChange"))

    selected_cell_color = property(_get_selected_cell_color, _set_selected_cell_color)

    def _get_division_wall_color(self):
        """
        Set the color used to draw the selected cell
        """
        return self._division_wall_color

    def _set_division_wall_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._division_wall_color:
            self._division_wall_color = col
            self.emit(SIGNAL("cellParameterChange"))

    division_wall_color = property(_get_division_wall_color, _set_division_wall_color)

    def _get_old_point_size(self):
        """
        Size of a old points on the scene
        """
        return self._old_point_size

    def _set_old_point_size(self, size):
        if size > 0 and size != self._old_point_size:
            self._old_point_size = size
            self.emit(SIGNAL("oldPointParameterChange"))

    old_point_size = property(_get_old_point_size, _set_old_point_size)

    def _get_old_point_color(self):
        """
        Color used to draw old points
        """
        return self._old_point_color

    def _set_old_point_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._old_point_color:
            self._old_point_color = col
            self.emit(SIGNAL("oldPointParameterChange"))

    old_point_color = property(_get_old_point_color, _set_old_point_color)

    def _get_old_point_matching_color(self):
        """
        Color used to draw old point matching the current hovered point
        """
        return self._old_point_matching_color

    def _set_old_point_matching_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._old_point_matching_color:
            self._old_point_matching_color = col
            self.emit(SIGNAL("oldPointParameterChange"))

    old_point_matching_color = property(_get_old_point_matching_color, _set_old_point_matching_color)

    def _get_arrow_line_size(self):
        """
        Width of the pen used to draw arrows.
        """
        return self._arrow_line_size

    def _set_arrow_line_size(self, size):
        if size>0 and size != self._arrow_line_size:
            self._arrow_line_size = size
            self.emit(SIGNAL("arrowParameterChange"))

    arrow_line_size = property(_get_arrow_line_size, _set_arrow_line_size)

    def _get_arrow_head_size(self):
        """
        Size of the arrow head in proportion to the length of the arrow
        """
        return self._arrow_head_size

    def _set_arrow_head_size(self, size):
        if 0 < size <= 1 and size != self._arrow_head_size:
            self._arrow_head_size = size
            self.emit(SIGNAL("arrowParameterChange"))

    arrow_head_size = property(_get_arrow_head_size, _set_arrow_head_size)

    def _get_arrow_color(self):
        """
        Color used to draw arrows
        """
        return self._arrow_color

    def _set_arrow_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._arrow_color:
            self._arrow_color = col
            self.emit(SIGNAL("arrowParameterChange"))

    arrow_color = property(_get_arrow_color, _set_arrow_color)

    def _get_draw_arrow(self):
        """
        Decide to make the arrows visible or not
        """
        return self._draw_arrow

    def _set_draw_arrow(self, value):
        value = bool(value)
        if value != self._draw_arrow:
            self._draw_arrow = value
            self.emit(SIGNAL("arrowParameterChange"))

    draw_arrow = property(_get_draw_arrow, _set_draw_arrow)

    def _get_use_OpenGL(self):
        """
        Force the use of OpenGL for rendering images
        """
        return self._use_OpenGL

    def _set_user_OpenGL(self, value):
        if value != self._use_OpenGL:
            self._use_OpenGL = value
            self.emit(SIGNAL("renderingChanged"))

    use_OpenGL = property(_get_use_OpenGL, _set_user_OpenGL)

    def _get_point_thickness(self):
        """Thickness of the line used to draw points"""
        return self._point_thickness

    def _set_point_thickness(self, value):
        value = int(value)
        if value >= 0 and self._point_thickness != value:
            self._point_thickness= value
            self.emit(SIGNAL("pointParameterChange"))

    def _del_point_thickness(self):
        del self._point_thickness

    point_thickness = property(_get_point_thickness, _set_point_thickness)

    def _get_old_point_thickness(self):
        """Thickness of the line used to draw old points"""
        return self._old_point_thickness

    def _set_old_point_thickness(self, value):
        value = int(value)
        if self._old_point_thickness != value:
            self._old_point_thickness = value
            self.emit(SIGNAL("oldPointParameterChange"))

    old_point_thickness = property(_get_old_point_thickness, _set_old_point_thickness)

    def _get_show_vectors(self):
        """Are the vectors from old to now points shown?"""
        return self._show_vectors

    def _set_show_vectors(self, value):
        self._show_vectors = value

    show_vectors = property(_get_show_vectors, _set_show_vectors, doc=_get_show_vectors.__doc__)

    def _get_link_views(self):
        """Link the viewports of the two panes in the main GUI"""
        return self._link_views

    def _set_link_views(self, value):
        self._link_views = value

    link_views = property(_get_link_views, _set_link_views, doc=_get_link_views.__doc__)

    def _get_show_template(self):
        """
        Whether the template should be shown or not

        :returntype: bool
        """
        return self._show_template

    def _set_show_template(self, value):
        if value != self._show_template:
            self._show_template = value
            self.emit(SIGNAL("searchParameterChange"))

    show_template = property(_get_show_template, _set_show_template)

    def _get_show_id(self):
        """
        If true, the id of the points should be shown as well.

        :returntype: bool
        """
        return self._show_id

    def _set_show_id(self, value):
        value = bool(value)
        if value != self._show_id:
            self._show_id = value
            self.emit(SIGNAL("pointParameterChange"))

    show_id = property(_get_show_id, _set_show_id)

    def _find_font(self):
        font = QFont()
        wanted_size = self._point_size
        font.setStyleStrategy(QFont.StyleStrategy(QFont.OpenGLCompatible|QFont.PreferAntialias))
        fm = QFontMetricsF(font)
        width = fm.width("888")
        ratio = 1.8*wanted_size/max(width, fm.ascent())
        self._font = font
        self._font_zoom = ratio

    def _get_font(self):
        """
        Font used to display the points id in the points.

        :returntype: `QFont`
        """
        return self._font

    font = property(_get_font)

    def _get_font_zoom(self):
        """
        Zoom used to display the points id in the points.

        :returntype: float
        """
        return self._font_zoom

    font_zoom = property(_get_font_zoom)
#}
#{ Search parameters

    def _get_estimate(self):
        """
        True if the copy functions estimate the position using normalized cross-correlation
        """
        return self._estimate

    def _set_estimate(self, value):
        self._estimate = bool(value)

    estimate = property(_get_estimate, _set_estimate)

    def _get_template_size(self):
        """
        Size of the template to search for (i.e. number of pixel around the position to extract)
        """
        return self._template_size

    def _set_template_size(self, size):
        size = int(size)
        if size > 0 and size != self._template_size:
            self._template_size = size
            self.template_rect = QRectF(-size, -size, 2*size, 2*size)
            if 1.5*size > self._search_size:
                self.search_size = int(ceil(1.5*size+0.1))
            self.emit(SIGNAL("searchParameterChange"))

    template_size = property(_get_template_size, _set_template_size)

    def _get_search_size(self):
        """
        Area around the point to look for the template
        """
        return self._search_size

    def _set_search_size(self, size):
        size = int(size)
        if size > self._template_size and size != self._search_size:
            self._search_size = size
            self.search_rect = QRectF(-size, -size, 2*size, 2*size)
            if size < 1.5*self._template_size:
                self.template_size = int(floor(2./3.*size-0.1))
            self.emit(SIGNAL("searchParameterChange"))

    search_size = property(_get_search_size, _set_search_size)

    def _get_search_color(self):
        """
        Color used to draw the searched area
        """
        return self._search_color

    def _set_search_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._search_color:
            self._search_color = col
            self.emit(SIGNAL("searchParameterChange"))

    search_color = property(_get_search_color, _set_search_color)

    def _get_template_color(self):
        """
        Color used to draw the template around a point
        """
        return self._template_color

    def _set_template_color(self, color):
        col = QColor(color)
        if col.isValid() and col != self._template_color:
            self._template_color = col
            self.emit(SIGNAL("searchParameterChange"))

    template_color = property(_get_template_color, _set_template_color)

    def _get_filter_size_ratio(self):
        """Ratio of the template size used to create the filter"""
        return self._filter_size_ratio

    def _set_filter_size_ratio(self, value):
        if value != self._filter_size_ratio:
            self._filter_size_ratio = value
            self.emit(SIGNAL("searchParameterChange"))

    filter_size_ratio = property(_get_filter_size_ratio, _set_filter_size_ratio)

    def _get_filter_size_ratio_percent(self):
        """Ratio of the template size used to create the filter in percent

        This property is garantied to return an integer"""
        return int(self._filter_size_ratio*100)

    def _set_filter_size_ratio_percent(self, value):
        self.filter_size_ratio = int(value)/100.0

    filter_size_ratio_percent = property(_get_filter_size_ratio_percent, _set_filter_size_ratio_percent)

    def _get_filter_size(self):
        """
        Size of the filter to use for the images
        """
        return int(self._template_size * self._filter_size_ratio)

    filter_size = property(_get_filter_size)

    def _get_estimate_position(self):
        """
        Boolean telling if the position of the points have to be estimated or just copied.

        :returntype: bool
        """
        return self._estimate_position

    def _set_estimate_position(self, value):
        self._estimate_position = value

    estimate_position = property(_get_estimate_position, _set_estimate_position, doc=_get_estimate_position.__doc__)
#}
#{ Main configuration

    def _get_last_dir(self):
        """Last directory used in file dialog box"""
        return self._last_dir

    def _set_last_dir(self, value):
        self._last_dir = value

    last_dir = property(_get_last_dir, _set_last_dir, doc =_get_last_dir.__doc__)

    def _get_cache_size(self):
        """Size of the image cache in MB"""
        return self._cache_size

    def _set_cache_size(self, value):
        self._cache_size = value
        import image_cache
        image_cache.cache.max_size = value

    cache_size = property(_get_cache_size, _set_cache_size, doc=_get_cache_size.__doc__)

    def _get_recent_projects(self):
        """List of the most recent projects loaded"""
        return self._recent_projects

    def _set_recent_projects(self, value):
        if self._recent_projects != value:
            self._recent_projects = value
            self.emit(SIGNAL("recentProjectsChange"))

    def add_recent_project(self, project):
        recent_projects = self._recent_projects
        if project in recent_projects:
            recent_projects.remove(project)
        recent_projects.insert(0,  project)
        while len(recent_projects) > self._max_number_of_projects:
            recent_projects.pop()
        self.emit(SIGNAL("recentProjectsChange"))

    recent_projects = property(_get_recent_projects, _set_recent_projects, doc=_get_recent_projects.__doc__)
#}
#{ User interaction parameters
    def _get_point_editable(self):
        """
        True if the points can be edited.

        :returntype: bool
        """
        return self._point_editable

    def _set_point_editable(self, value):
        value = bool(value)
        if value != self._point_editable:
            self._point_editable = value
            self.emit(SIGNAL("pointParameterChange"))

    is_point_editable = property(_get_point_editable, _set_point_editable)

    def _get_point_selectable(self):
        """
        True if the cells can be selected.

        :returntype: bool
        """
        return self._point_selectable

    def _set_point_selectable(self, value):
        value = bool(value)
        if value != self._point_selectable:
            self._point_selectable = value
            self.emit(SIGNAL("pointParameterChange"))

    is_point_selectable = property(_get_point_selectable, _set_point_selectable)

    def _get_cell_editable(self):
        """
        True if the cells can be edited.

        :returntype: bool
        """
        return self._cell_editable

    def _set_cell_editable(self, value):
        value = bool(value)
        if value != self._cell_editable:
            self._cell_editable = value
            self.emit(SIGNAL("cellParameterChange"))

    is_cell_editable = property(_get_cell_editable, _set_cell_editable)
#}

#{ Growth representation parameters
    def _get_walls_coloring(self):
        """
        Mode used to color walls.

        :returntype: `str`
        """
        return self._walls_coloring

    def _set_walls_coloring(self, value):
        value = str(value)
        if value != self._walls_coloring:
            self._walls_coloring = value
            self.emit(SIGNAL("plottingParameterChange"))

    walls_coloring = property(_get_walls_coloring, _set_walls_coloring)

    def _get_walls_symetric_coloring(self):
        """
        True if the coloring scheme must be symetric around 0.

        :returntype: bool
        """
        return self._walls_symetric_coloring

    def _set_walls_symetric_coloring(self, value):
        value = bool(value)
        if value != self._walls_symetric_coloring:
            self._walls_symetric_coloring = value
            self.emit(SIGNAL("plottingParameterChange"))

    walls_symetric_coloring = property(_get_walls_symetric_coloring, _set_walls_symetric_coloring)

    def _get_walls_cap_values(self):
        '''
        True if the values used to color the walls must be caped.

        :returntype: bool
        '''
        return self._walls_cap_values

    def _set_walls_cap_values(self, value):
        if self._walls_cap_values != value:
            self._walls_cap_values = value
            self.emit(SIGNAL("plottingParameterChange"))

    walls_cap_values = property(_get_walls_cap_values, _set_walls_cap_values)

    def _get_walls_values_min(self):
        '''
        Minimum cap.

        :returntype: float
        '''
        return self._walls_values_min

    def _set_walls_values_min(self, value):
        value = float(value)
        if self._walls_values_min != value:
            self._walls_values_min = value
            self.emit(SIGNAL("plottingParameterChange"))

    walls_values_min = property(_get_walls_values_min, _set_walls_values_min)

    def _get_walls_values_max(self):
        '''
        Maximum cap.

        :returntype: float
        '''
        return self._walls_values_max

    def _set_walls_values_max(self, value):
        value = float(value)
        if self._walls_values_max != value:
            self._walls_values_max = value
            self.emit(SIGNAL("plottingParameterChange"))

    walls_values_max = property(_get_walls_values_max, _set_walls_values_max)

    def _get_cells_coloring(self):
        """
        Mode used to color cells

        :returntype: `str`
        """
        return self._cells_coloring

    def _set_cells_coloring(self, value):
        value = str(value)
        if value != self._cells_coloring:
            self._cells_coloring = value
            self.emit(SIGNAL("plottingParameterChange"))

    cells_coloring = property(_get_cells_coloring, _set_cells_coloring)

    def _get_cells_symetric_coloring(self):
        """
        True if the coloring scheme must be symetric around 0.

        :returntype: bool
        """
        return self._cells_symetric_coloring

    def _set_cells_symetric_coloring(self, value):
        value = bool(value)
        if value != self._cells_symetric_coloring:
            self._cells_symetric_coloring = value
            self.emit(SIGNAL("plottingParameterChange"))

    cells_symetric_coloring = property(_get_cells_symetric_coloring, _set_cells_symetric_coloring)

    def _get_cells_cap_values(self):
        '''
        True if the values used to color the cells must be caped.

        :returntype: bool
        '''
        return self._cells_cap_values

    def _set_cells_cap_values(self, value):
        value = bool(value)
        if self._cells_cap_values != value:
            self._cells_cap_values = value
            self.emit(SIGNAL("plottingParameterChange"))

    cells_cap_values = property(_get_cells_cap_values, _set_cells_cap_values)

    def _get_cells_values_min(self):
        '''
        Minimum cap.

        :returntype: float
        '''
        return self._cells_values_min

    def _set_cells_values_min(self, value):
        value = float(value)
        if self._cells_values_min != value:
            self._cells_values_min = value
            self.emit(SIGNAL("plottingParameterChange"))

    cells_values_min = property(_get_cells_values_min, _set_cells_values_min)

    def _get_cells_values_max(self):
        '''
        Maximum cap.

        :returntype: float
        '''
        return self._cells_values_max

    def _set_cells_values_max(self, value):
        value = float(value)
        if self._cells_values_max != value:
            self._cells_values_max = value
            self.emit(SIGNAL("plottingParameterChange"))

    cells_values_max = property(_get_cells_values_max, _set_cells_values_max)

    def _get_ellipsis_scaling(self):
        '''
        Scaling applied to the kmin and kmaj to plot the ellipsis

        :returntype: float
        '''
        return self._ellipsis_scaling

    def _set_ellipsis_scaling(self, value):
        value = float(value)
        if self._ellipsis_scaling != value:
            self._ellipsis_scaling = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_scaling = property(_get_ellipsis_scaling, _set_ellipsis_scaling)

    def _get_ellipsis_color(self):
        '''
        Color used to draw the ellipsis.

        :returntype: `QColor`
        '''
        return self._ellipsis_color

    def _set_ellipsis_color(self, value):
        value = QColor(value)
        if self._ellipsis_color != value:
            self._ellipsis_color = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_color = property(_get_ellipsis_color, _set_ellipsis_color)

    def _get_ellipsis_thickness(self):
        '''
        Thickness used to draw the growth tensor ellipsis

        :returntype: int
        '''
        return self._ellipsis_thickness

    def _set_ellipsis_thickness(self, value):
        value = int(value)
        if self._ellipsis_thickness != value:
            self._ellipsis_thickness = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_thickness = property(_get_ellipsis_thickness, _set_ellipsis_thickness)

    def _get_ellipsis_min_anisotropy(self):
        '''
        Minimum anisotropy required to draw axes of an ellipsis.

        :returntype: float
        '''
        return self._ellipsis_min_anisotropy

    def _set_ellipsis_min_anisotropy(self, value):
        value = float(value)
        if self._ellipsis_min_anisotropy != value:
            self._ellipsis_min_anisotropy = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_min_anisotropy = property(_get_ellipsis_min_anisotropy, _set_ellipsis_min_anisotropy)

    def _get_ellipsis_positive_color(self):
        '''
        Color used to draw growth tensor ellipsis axis if the value is positive.

        :returntype: `QColor`
        '''
        return self._ellipsis_positive_color

    def _set_ellipsis_positive_color(self, value):
        value = QColor(value)
        if self._ellipsis_positive_color != value:
            self._ellipsis_positive_color = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_positive_color = property(_get_ellipsis_positive_color, _set_ellipsis_positive_color)

    def _get_ellipsis_negative_color(self):
        '''
        Color used to draw growth tensor ellipsis axis if the value is negative.

        :returntype: `QColor`
        '''
        return self._ellipsis_negative_color

    def _set_ellipsis_negative_color(self, value):
        value = QColor(value)
        if self._ellipsis_negative_color != value:
            self._ellipsis_negative_color = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_negative_color = property(_get_ellipsis_negative_color, _set_ellipsis_negative_color)

    def _get_ellipsis_plot(self):
        '''True if the ellipsis is to be plotted.

        :returntype: bool'''
        return self._ellipsis_plot

    def _set_ellipsis_plot(self, value):
        value = bool(value)
        if self._ellipsis_plot != value:
            self._ellipsis_plot = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_plot = property(_get_ellipsis_plot, _set_ellipsis_plot)

    def _get_ellipsis_scale_axis(self):
        '''True if the ellipsis is to be plotted.

        :returntype: bool'''
        return self._ellipsis_scale_axis

    def _set_ellipsis_scale_axis(self, value):
        value = bool(value)
        if self._ellipsis_scale_axis != value:
            self._ellipsis_scale_axis = value
            self.emit(SIGNAL("plottingParameterChange"))

    ellipsis_scale_axis = property(_get_ellipsis_scale_axis, _set_ellipsis_scale_axis)

    def _get_growth_cell_color(self):
        '''
        Color used to draw cells without function.

        :returntype: `QColor`
        '''
        return self._growth_cell_color

    def _set_growth_cell_color(self, value):
        value = QColor(value)
        if self._growth_cell_color != value:
            self._growth_cell_color = value
            self.emit(SIGNAL("plottingParameterChange"))

    growth_cell_color = property(_get_growth_cell_color, _set_growth_cell_color)

    def _get_growth_wall_color(self):
        '''
        Color used to draw walls without function.

        :returntype: `QColor`
        '''
        return self._growth_wall_color

    def _set_growth_wall_color(self, value):
        value = QColor(value)
        if self._growth_wall_color != value:
            self._growth_wall_color = value
            self.emit(SIGNAL("plottingParameterChange"))

    growth_wall_color = property(_get_growth_wall_color, _set_growth_wall_color)

    def _get_growth_cell_function(self):
        '''
        Transfer function used to draw cells. This is actually the pickled form of the transfer function.

        :returntype: `str`
        '''
        return self._growth_cell_function

    def _set_growth_cell_function(self, value):
        if self._growth_cell_function != value:
            self._growth_cell_function = value
            self.emit(SIGNAL("plottingParameterChange"))

    growth_cell_function = property(_get_growth_cell_function, _set_growth_cell_function)

    def _get_growth_wall_function(self):
        '''
        Transfer function used to draw walls. This is actually the pickled form of the transfer function.

        :returntype: `str`
        '''
        return self._growth_wall_function

    def _set_growth_wall_function(self, value):
        if self._growth_wall_function != value:
            self._growth_wall_function = value
            self.emit(SIGNAL("plottingParameterChange"))

    growth_wall_function = property(_get_growth_wall_function, _set_growth_wall_function)
#}

def createParameters():
    if QCoreApplication.startingUp():
        raise ImportError("The parameters module has been loaded before the creation of a Qt application")
    global instance
    if instance is None:
        instance = Parameters()
    else:
        instance.load()

def saveParameters():
    global instance
    instance.save()

# To be instantiated after Qt has been initialized
instance = None
#createParameters()

