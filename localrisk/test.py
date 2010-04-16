import Image
from Tkinter import Label, Tk, Frame, PhotoImage
map = Image.open('intel.png')
map.convert('RGB').convert('P', palette=Image.ADAPTIVE)
#map.show()
map.save('isintel.gif')

cordinatesMap = {"USA":(100,100),"England":(50,200)}

chooseQueue = []

root=Tk()
photo = PhotoImage(file='isintel.gif')
def callback(event):
    print "clicked at", event.x, event.y
    maxDist = 100
    match = None
    for entry in cordinatesMap:
        print 'checking',entry
        cor = cordinatesMap[entry]
        print 'cordinates',cor
        dist = abs(event.x-cor[0])+abs(event.y-cor[1])
        print 'distance',dist
        if dist<maxDist:
            match = entry
            maxDist = dist
    print match, dist
    
    checkForAction()

def checkForAction():
    print 'hey'
    if chooseQueue:
        if 1: # mode is correct
        

label = Label(root, image=photo)
label.image = photo
label.bind("<Button-1>", callback)
label.pack()
root.mainloop()



