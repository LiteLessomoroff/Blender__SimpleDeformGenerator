import bpy
import json
from .MeshUtils import MeshesManipulator, MeshesTransformedContainer, MeshesTransformedContainer__of__MeshesSimpleDeformator, MeshesSimpleDeformator
from .DefaultParams import DEFAULT_PARAMS

bl_info = {
    "name": "SimpleDeforms panel",
    "author": "Evgeniy Tikhonov",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "object.SimpleDeforms_1c574fcd6f7a4a4f8fd6ff45be9e7f79",
    "description": "Generates many version or simpleDeforms applied to selected objects",
    "warning": "",
    "doc_url": "",
    "category": "Mesh manipulation",
}

class SimpleDeformsProperties(bpy.types.PropertyGroup):
    REMESH_P : bpy.props.StringProperty(name='Remesh method and params', default=str(json.dumps(DEFAULT_PARAMS["remesh_p"])))
    LST_DEFORMS : bpy.props.StringProperty(name='Deforms method and params', default=str(json.dumps(DEFAULT_PARAMS["lst_deforms"])))
    NEED_REMESH : bpy.props.BoolProperty(name='Remesh before deformation', default=DEFAULT_PARAMS["need_remesh"])
    APPLY_MODIFIERS : bpy.props.BoolProperty(name='Apply modifiers', default=DEFAULT_PARAMS["apply_modifiers"])

class SimmpleDeforms_OT_versions_gen(bpy.types.Operator):
    bl_idname = "simpledeforms.versions_gen"
    bl_label = "Generates N versions of simpleDeforms"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context) -> set:
        scene = context.scene
        myprops = scene.my_props_simpleDeforms_panel

        apply_modifiers = myprops.APPLY_MODIFIERS
        need_remesh = myprops.NEED_REMESH
        remesh_p = json.loads(myprops.REMESH_P)
        lst_deforms = json.loads(myprops.LST_DEFORMS)
        selected = bpy.context.selected_objects

        pipeline_params={"remesh_p" : remesh_p, "lst_deforms" : lst_deforms, "apply_modifiers": apply_modifiers, "need_remesh" : need_remesh}                

        mtc = MeshesTransformedContainer__of__MeshesSimpleDeformator(meshes=selected, new_collection_prefix="SimpleDeformation_", pipeline_params=pipeline_params)
        msd = MeshesSimpleDeformator()
        mtc.addTransformedMeshes(msd.genDeforms(mtc))
        return {'FINISHED'}


class SimmpleDeformsOperatorUI(bpy.types.Panel):
    bl_label = "Simple deforms to selected"
    bl_idname = "MySimpleUIDeforms"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"


    def draw(self, context) -> None:
        layout = self.layout
        scene = context.scene
        myprops = scene.my_props_simpleDeforms_panel
        layout.prop(myprops, "REMESH_P")
        row = layout.row()
        layout.prop(myprops, "LST_DEFORMS")
        row = layout.row()
        layout.prop(myprops, "APPLY_MODIFIERS")
        row = layout.row()
        layout.prop(myprops, "NEED_REMESH")
        row = layout.row()        
        row.operator("simpleDeforms.versions_gen")

classes = [SimpleDeformsProperties, SimmpleDeforms_OT_versions_gen, SimmpleDeformsOperatorUI]

def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.my_props_simpleDeforms_panel = bpy.props.PointerProperty(type=SimpleDeformsProperties)


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.my_props_simpleDeforms_panel

if __name__ == "__main__":
    register()
