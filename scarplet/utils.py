# -*- coding: utf-8
""" Utility classes and funcitons for template matching framework. """


class BoundingBox(object):

    def __init__(self, lr, ul):

        self.lrx = lr[0]
        self.lry = lr[1]
        self.lr = lr

        self.ulx = ul[0]
        self.uly = ul[1]
        self.ul = ul

        self.llx = ul[0]
        self.lly = lr[1]
        self.ll = (self.llx, self.lly)

        self.urx = lr[0]
        self.ury = ul[1]
        self.ur = (self.urx, self.ury)

        self.corners = [self.ul, self.ll, self.ur, self.lr]

    def contains(self, point):

        intersect_x = point[0] >= self.ulx and point[0] <= self.lrx
        intersect_y = point[1] >= self.lry and point[1] <= self.uly

        return intersect_x and intersect_y

    def intersects(self, bbox):

        for corner in bbox.corners:
            if self.contains(corner):
                return True

        for corner in self.corners:
            if bbox.contains(corner):
                return True

        return False
