import torch
import copy

try :
    from model import ChessModel
except:
    from ia.ml.model import ChessModel


class Builder:
    def __init__(self, component_dict):
        """
        Initialize the Builder with a dictionary of components.

        Args:
            component_dict (dict): Dictionary of components.
        """
        self.component_dict = component_dict

    def __call__(self, component_name, *args, **kwargs):
        """
        Create an instance of the specified component.

        Args:
            component_name (str): Name of the component.
            *args: Positional arguments for the component.
            **kwargs: Keyword arguments for the component.

        Returns:
            object: Instance of the specified component.
        """
        if component_name not in self.component_dict:
            raise ValueError(f"Component {component_name} is not found in the available components.")
        return self.component_dict[component_name](*args, **kwargs)


def build_model(architecture, variables, encoded_moves):
    """
    Build the model based on the specified architecture.

    Args:
        architecture (list): List of layers in the architecture.
        variables (dict): Dictionary of variables.
        encoded_moves (dict): Dictionary of encoded moves.

    Returns:
        ChessModel: The constructed model.
    """
    builder = Builder(torch.nn.__dict__)
    layers = []
    
    for block in architecture:
        assert len(block) == 1, "Each block in the architecture should be a single layer."
        name, kwargs = list(block.items())[0]
        if kwargs is None:
            kwargs = {}
        args = kwargs.pop("args", [])

        args = [variables.get(arg, arg) for arg in args]
        kwargs = {k: variables.get(v, v) for k, v in kwargs.items()}

        layers.append(builder(name, *args, **kwargs))

    layers = torch.nn.ModuleList(layers)

    return ChessModel(layers, encoded_moves)


def build_optimizer(config, model_params, variables):
    """
    Build the optimizer based on the specified configuration.

    Args:
        config (dict): Configuration of the optimizer.
        model_params (iterable): Parameters of the model.
        variables (dict): Dictionary of variables.

    Returns:
        torch.optim.Optimizer: The constructed optimizer.
    """
    builder = Builder(torch.optim.__dict__)

    optimizer_name, kwargs = list(config.items())[0]

    if kwargs is None:
        kwargs = {}

    args = kwargs.pop("args", [])
    args = [variables.get(arg, arg) for arg in args]
    kwargs["params"] = model_params

    return builder(optimizer_name, *args, **kwargs)

