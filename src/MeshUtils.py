import bpy
import bpy_types
import datetime
import math
import uuid
from mathutils import Vector

class MeshesManipulator:
    "Simple operations with list of meshes"
    def set_selected(self, lst:list[bpy_types.Object], state: bool) -> int:
        "For each meshes in lst - select/deselect all of them"
        cnt_selected = 0        
        for l in lst:
            try:
                l.select_set(state)
                cnt_selected += 1
            except Exception as ex:
                pass
        if state == True:
            bpy.context.view_layer.objects.active = lst[0]
        return cnt_selected    
    def duplicate(self, lst: list[bpy_types.Object], collection:bpy_types.Collection=None, new_location=None, mesh_prefix: str="mesh_") -> list[bpy_types.Object]:
        "For each meshes in lst - duplicate all of them"
        lst_copy = []                
        for id in range(0, len(lst)):
            new_l = lst[id].copy()
            mesh_name = mesh_prefix + str(uuid.uuid4().hex)
            new_l.data.name = mesh_name
            new_l.name = mesh_name
            if new_location:
                new_l.location = new_location
            lst_copy.append(new_l)
        if collection != None:
            for l in lst_copy:
                collection.objects.link(l)
        return lst_copy        
    def remove_list(self, lst:list[bpy_types.Object]=None) -> int:        
        "For each meshes in lst - remove all of them from scene"
        objs = bpy.data.objects
        cnt_removed = 0
        for l in lst:
            try:
                objs.remove(objs[l.name], do_unlink=True)
                cnt_removed += 1
            except Exception as ex:
                pass
        return cnt_removed

class MeshesTransformedContainer:
    "Container with source meshes and list of modified meshes with collection for them"
    def __init__(self, meshes:list[bpy_types.Object], collection:bpy_types.Collection=None, new_collection_prefix:str="Collection_", pipeline_params:dict=None) -> None:    
        try:    
            self.meshes = filter(lambda x: x.type == 'MESH', meshes)
        except Exception as ex:
            raise Exception("meshes:" + str(meshes) + "\nex:" + str(ex))
        self.meshes = list(self.meshes)
        self.meshes_transformed = []
        if not collection:
            self.collection = bpy.context.blend_data.collections.new(name=new_collection_prefix + datetime.datetime.now().isoformat() )
            bpy.context.collection.children.link(self.collection)
        else:
            self.collection = collection
        self.pipeline_params = pipeline_params
    def addTransformedMeshes(self,lst:list[bpy_types.Object]=None) -> bool:        
        "Extend modified meshes"
        if lst:
            self.meshes_transformed.extend(lst)
            return True
        return False

class MeshesTransformedContainer__of__MeshesSimpleDeformator(MeshesTransformedContainer):
    "For 'simple deformation' - it is an important to calculate radians instead of degrees"
    def __init__(self, meshes:list[bpy_types.Object], collection=None, new_collection_prefix:str="Collection_", pipeline_params:dict=None):
        super().__init__(meshes, collection, new_collection_prefix, pipeline_params)
        for l in self.pipeline_params["lst_deforms"]:
            try:
                l["angle"] = math.radians(float(l["angle"]))
            except Exception as ex:
                pass
            
class MeshesSimpleDeformator:                     
    def genDeforms(self, mtc: MeshesTransformedContainer) -> None:
        """ Pipeline for simeple deformation.
        Gen copy of source mesh -> remesh it(if option set) ->
        gen copy of mesh from prev modification(remesh if was set) by deform settings times"""   
        try:
            mm = MeshesManipulator()
            draft_meshes = []
            for m in mtc.meshes:
                draft_meshes += mm.duplicate([m], mtc.collection, None)
            if mtc.pipeline_params["need_remesh"]:
                self._applyRemesh(draft_meshes, mtc.pipeline_params["remesh_p"])
            res = self._applySimpleDeforms(draft_meshes, mtc.pipeline_params["lst_deforms"], mtc.collection)                
            mm.remove_list(draft_meshes)
        except Exception as ex:
            raise Exception("Error when genDeforms!\n" + str(ex))
        
    def _genLocation(self, obj:bpy_types.Object) -> Vector:
        "Just way to get result without overlapping"
        return obj.location + obj.dimensions * 2
    def _applyRemesh(self, meshes:list[bpy_types.Object], remesh_p: dict):
        "Remesh source mesh for successful deformation(if small dencity)"
        mm = MeshesManipulator()    
        for s in meshes:
            try:
                mm.set_selected(bpy.context.selected_objects, False)
                mm.set_selected([s], True)
                bpy.ops.object.modifier_add(type='REMESH')
                modifier = list(filter(lambda x: x.type == 'REMESH', s.modifiers))[-1]
                for r in remesh_p:
                    setattr(modifier, r, remesh_p[r])
                bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)                
            except Exception as ex:
                pass
        mm.set_selected(bpy.context.selected_objects, False)        
    def _applySimpleDeforms(self, meshes:list[bpy_types.Object], lst_deforms: dict, collection=None, apply_modifiers: bool=False) -> list:
        "Generate deforms for meshes"
        mm = MeshesManipulator()
        meshes_transformed = []
        for deform in lst_deforms:
            for m in meshes:
                try:
                    new_m = mm.duplicate([m], collection, self._genLocation(m))[0]
                    meshes_transformed.append(new_m)
                    mm.set_selected(bpy.context.selected_objects, False)
                    mm.set_selected([new_m], True)
                    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')                    
                    modifier = list(filter(lambda x: x.type == 'SIMPLE_DEFORM', new_m.modifiers))[-1]
                    for el in deform:
                        setattr(modifier, el, deform[el])
                    if apply_modifiers:                        
                        bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
                except Exception as ex:
                    pass
            mm.set_selected(bpy.context.selected_objects, False)
        return meshes_transformed
