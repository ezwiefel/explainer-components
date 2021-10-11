<!--
 Copyright (c) 2021 Microsoft

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

# SHAP Kernel Explainer Component for Azure ML Designer

Creates (and uploads to AML) a model explaination for two-class classification models using the SHAP KernelExplainer from the [interpret-community](https://pypi.org/project/interpret-community) Python package.

## Registering Component

To add this component to your AML Designer Workspace:

1. Under "Assets" in the left-side menu, select "Components"<br>
   <img src="media/assets_components.png" alt="Assets and Components menu view" width=150><br>
1. Next, click "New Component"<br>
   <img src="media/new_component.png" alt="New Component Button" width=300><br>
1. Finally, in the Register Components screen, choose Github Repo and enter the url `https://github.com/ezwiefel/explainer-components/blob/main/two-class-shap-explainer/explainer_module.yml` <br>
   <img src="media/register_component.png" alt="Register Component Screen" width=500><br>

## Using the SHAP Kernel Explainer in AML Designer

After these steps, you'll be able to find a new module under the 'Custom Components' area in AML Designer.<br>
<img src="media/custom_component.png" alt="Custom Component" width=300><br>
