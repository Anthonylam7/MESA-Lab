from numpy.matrixlib import mat, matrix
from numpy import matmul
from math import cos, sin



class VectorObject(object):
    '''
    class to represent 3d objects as points in a matrix
    operations involve multiplying by a 4 by 4 rotation or translation matrix outlined in https://www.fastgraph.com/makegames/3drotation/

    Numpy is used to convert python 2d list into matrix objects
    '''
    def __init__(self, coordinates, center=[0,0,0,0]):
        super(VectorObject, self).__init__()
        self.points = coordinates
        self.center = center
        self.check_points()
        self.points = mat(coordinates)

    def check_points(self):
        '''
        func checks sublist is of length 4
        if less than length 4 then the elements are assumed to be x,y,z,0 in order
        if greater then 4 then an error is thrown because coordinates are indeterminate from user input
        :return:
        '''

        for row in self.points:
            while len(row) < 4:
                row.append(0)
        return

    def build_rotatation_matrix(self, axis, angle):
        '''
        :param angle: the angle to rotate by
        :param axis: tuple (x,y,z) unit vector defining axis of rotation
        :return: numpy matrix rotation
        '''
        angle = angle/180*3.14159
        if axis == (1,0,0):
            return mat(
                [
                    [1, 0, 0, 0],
                    [0, cos(angle), -sin(angle), 0],
                    [0, sin(angle), cos(angle), 0],
                    [0, 0, 0, 1]
                ]
            )
        elif axis == (0,1,0):
            return mat(
                [
                    [cos(angle), 0, sin(angle), 0],
                    [0, 1, 0, 0],
                    [-sin(angle), 0, cos(angle), 0],
                    [0, 0, 0, 1]
                ]
            )
        elif axis == (0,0,1):
            return mat(
                [
                    [cos(angle), -sin(angle), 0, 0],
                    [sin(angle), cos(angle), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
                ]
            )
        else:
            if len(axis) != 3:
                raise ValueError('Axis is a tuple of length 3')
            else:
                raise  ValueError('Axis is a unit vector in the x, y, or z dir')

    def transform(self, operation, axis, magnitude):
        if operation == 'rotate':
            for i,row in enumerate(self.points):
                self.points[i] = row - self.center
            transform = self.build_rotatation_matrix(axis, magnitude)
            self.points = matmul(self.points, transform)
            for i,row in enumerate(self.points):
                self.points[i] = row + self.center
            return self.points
        elif operation == 'translate':
            # need to add translation method
            return

    def to_list(self):
        return self.points.tolist()




if __name__ == '__main__':
    v = VectorObject( [[1,2,3,0],[4,5,6,0],[0,0,1,0],[8,2,3,0]], (1,0,0,0) )
    v.transform('rotate', (0, 1, 0), 90)
    print( v.points.tolist() )