import copy
import torch

try:
    from model import ChessModel
except ImportError:
    from ia.ml.model import ChessModel 
    
class Builder:
    """
    A generic factory class to instantiate objects from a given dictionary of components.
    """
    def __init__(self, component_dict: dict[str, type]):
        """
        Initialize the Builder with a dictionary of components.

        Args:
            component_dict (dict[str, type]): Dictionary mapping component names to their constructors.
        """
        self.component_dict: dict[str, type] = component_dict

    def __call__(self, component_name: str, *args: list, **kwargs: dict) -> object:
        """
        Create an instance of the specified component.

        Args:
            component_name (str): Name of the component to instantiate.
            *args (list): Positional arguments for the component constructor.
            **kwargs (dict): Keyword arguments for the component constructor.

        Returns:
            object: An instance of the specified component.
        
        Raises:
            ValueError: If the component is not found in the component dictionary.
        """
        if component_name not in self.component_dict:
            raise ValueError(f"Component {component_name} is not found in the available components.")
        return self.component_dict[component_name](*args, **kwargs)

def build_model(architecture: list[dict[str, dict | None]], variables: dict[str, object], encoded_moves: dict[str, object], color: int) -> ChessModel:
    """
    Construct a neural network model based on a specified architecture.

    Args:
        architecture (list[dict[str, dict | None]]): List of layer definitions, where each entry is a dictionary specifying a layer name and its parameters.
        variables (dict[str, object]): Dictionary of named variables to replace placeholders in the layer parameters.
        encoded_moves (dict[str, object]): Dictionary containing encoded move representations for the model.
        color (int): The color of the player.

    Returns:
        ChessModel: The constructed model containing the specified architecture.
    """
    builder = Builder(torch.nn.__dict__)
    layers: list[torch.nn.Module] = []
    
    for block in architecture:
        assert len(block) == 1, "Each block in the architecture should define a single layer."
        name, kwargs = list(block.items())[0]
        
        if kwargs is None:
            kwargs = {}
        
        args: list = kwargs.pop("args", [])
        args = [variables.get(arg, arg) for arg in args]
        kwargs = {k: variables.get(v, v) for k, v in kwargs.items()}

        layers.append(builder(name, *args, **kwargs))

    layers = torch.nn.ModuleList(layers)
    return ChessModel(layers, encoded_moves, color)

def build_optimizer(config: dict[str, dict | None], model_params: torch.nn.ParameterList, variables: dict[str, object]) -> torch.optim.Optimizer:
    """
    Construct an optimizer for training the model based on a given configuration.

    Args:
        config (dict[str, dict | None]): Dictionary specifying the optimizer type and its parameters.
        model_params (torch.nn.ParameterList): Iterable containing the model's parameters to be optimized.
        variables (dict[str, object]): Dictionary of named variables to replace placeholders in the optimizer parameters.

    Returns:
        torch.optim.Optimizer: The instantiated optimizer object.
    """
    builder = Builder(torch.optim.__dict__)
    optimizer_name, kwargs = list(config.items())[0]
    
    if kwargs is None:
        kwargs = {}
    
    args: list = kwargs.pop("args", [])
    args = [variables.get(arg, arg) for arg in args]
    kwargs["params"] = model_params
    
    return builder(optimizer_name, *args, **kwargs)
