## Programming assignment 4 Zhizhou Xing CS680
I have worked on this assignment individually, I did not consult or colloborate with anyone.

### Summary

This assignment is the most challenging in the part of using parametized formula to draw 3D shapes. finding the right way to sort each vertices and their normal to VBO is challenging. 
I have to logically and experimentally to find out the right direction for the normal.

### Illumination model

I always use the infinite lighting as the light source for ambient light, and only one infinite light is chosen for ambient light. For specular, we ignore any diffuse contribution if N dot L is smaller than zero, as well as specular(we also check for V dot R to be bigger than cos(allowed angle))

I have also added feature to toggle on and off light source, as well as each type of contribution

### light source

I have used the formula to correctly construct point light, infinite light and spot light(with attenuation). Construct simply using the formula. The logic is that if no infinite light direction or radial light direction is given it is point light. The attenuation is correctly performed using the given parameter.  

