import json
from io import StringIO
from multiprocessing import Process
from typing import Any

from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from yawning_titan.db.doc_metadata import DocMetadata
from yawning_titan.game_modes.game_mode import GameMode
from yawning_titan.networks import network_creator
from yawning_titan.networks.network import Network
from yawning_titan_gui.forms.game_mode_forms import (
    GameModeForm,
    GameModeFormManager,
    GameModeSection,
)
from yawning_titan_gui.forms.network_forms import (
    NetworkFormManager,
    NetworkTemplateForm,
)
from yawning_titan_gui.helpers import GameModeManager, NetworkManager, get_sidebar

default_toolbar = {
    "home": {"icon": "bi-house-door", "title": "Home"},
    "random-elements": {"icon": "bi-gear", "title": "Set random elements"},
    "network-nodes": {"icon": "bi-diagram-2", "title": "Network nodes"},
    # "run-config-set": {"icon": "bi-collection-play", "title": "Run config"},
    # "run-view": {"icon": "bi-play", "title": "Run game"},
}

protected_game_mode_ids = ["base_config.yaml"]

class HomeView(View):
    """Django page template for landing page."""

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Handle page get requests.

        :param request: the Django page `request` object containing the html data for `home.html` and the server GET / POST request bodies.
        """
        return self.render_page(request)

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle page post requests.

        :param request: the Django page `request` object containing the html data for `home.html` and the server GET / POST request bodies.
        """
        return self.render_page(request)

    def render_page(self, request: HttpRequest):
        """Process pythonic tags in home.html and return formatted page."""
        return render(
            request,
            "home.html",
            {
                "sidebar": get_sidebar(),
                "toolbar": default_toolbar
            },
        )


class DocsView(View):
    """
    Django representation of home.html.

    implements 'get' and 'post' methods to handle page requests.
    """

    def get(self, request: HttpRequest, section:str, *args, **kwargs):
        """
        Handle page get requests.

        :param request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """        
        return render(
            request,
            "docs.html",
            # {"sidebar": get_sidebar(),"doc_url":f"http://localhost:8080/source/{section}.html"},
            {"sidebar": get_sidebar(),"doc_url":reverse(f"docs {section}")},
        )

    def post(self, request: HttpRequest, section:str, *args, **kwargs):
        """Handle page post requests.

        :param request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        return render(
            request,
            "docs.html",
            {"sidebar": get_sidebar()},
        )


class GameModesView(View):
    """Django page template for game mode management."""

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Handle page get requests.

        :param: request: the Django page `request` object containing the html data for `game_modes.html` and the server GET / POST request bodies.
        """
        dialogue_boxes = [
            {
                "id": "delete-dialogue",
                "message": "Are you sure you want to delete the selected game modes(s)?\n\nThis action cannot be undone.",
                "actions": ["Delete game mode"],
            },
            {
                "id": "create-dialogue",
                "header": "Create new game mode",
                "message": "Enter a name for your new game mode",
                "actions": ["Create"],
                "input_prompt": "Game mode name...",
            },
            {
                "id": "create-from-dialogue",
                "header": "Create game mode from",
                "message": "Enter a name for your new game mode",
                "actions": ["Create game mode"],
                "input_prompt": "Game mode name...",
            },
        ]
        return render(
            request,
            "game_modes.html",
            {
                "sidebar": get_sidebar(),
                "dialogue_boxes": dialogue_boxes,
                "game_modes": GameModeManager.get_game_mode_data(),
            },
        )


class NetworksView(View):
    """Django page template for network management."""

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Handle page get requests.

        :param: request: the Django page `request` object containing the html data for `networks.html` and the server GET / POST request bodies.
        """
        networks = NetworkManager.db.all()
        range_bound_items = [
            {
                "name": "entry_nodes",
                "min": min(
                    [
                        len(network.entry_nodes) if network.entry_nodes else 0
                        for network in networks
                    ]
                ),
                "max": max(
                    [
                        len(network.entry_nodes) if network.entry_nodes else 0
                        for network in networks
                    ]
                ),
            },
            {
                "name": "high_value_nodes",
                "min": min(
                    [
                        len(network.high_value_nodes) if network.high_value_nodes else 0
                        for network in networks
                    ]
                ),
                "max": max(
                    [
                        len(network.high_value_nodes) if network.high_value_nodes else 0
                        for network in networks
                    ]
                ),
            },
            {
                "name": "network_nodes",
                "min": min([len(network.nodes) for network in networks]),
                "max": max([len(network.nodes) for network in networks]),
            },
        ]
        dialogue_boxes = [
            {
                "id": "delete-dialogue",
                "message": "Are you sure you want to delete the selected network(s)?\n\nThis action cannot be undone.",
                "actions": ["Delete network"],
            },
            {
                "id": "create-dialogue",
                "header": "Create new network",
                "message": "Enter a name for your new network",
                "actions": ["Template network", "Custom network"],
                "input_prompt": "Network name...",
            },
            {
                "id": "create-from-dialogue",
                "header": "Create network from",
                "message": "Enter a name for your new network",
                "actions": ["Create network"],
                "input_prompt": "Network name...",
            },
        ]
        return render(
            request,
            "networks.html",
            {
                "sidebar": get_sidebar(),
                "networks": [network.doc_metadata for network in networks],
                "range_bound_items": range_bound_items,
                "dialogue_boxes": dialogue_boxes,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        """Handle page get requests.

        :param request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        if request.method == "POST":
            return JsonResponse(
                {
                    "ids": NetworkManager.filter(
                        request.POST.get("attribute"),
                        request.POST.get("min"),
                        request.POST.get("max"),
                    )
                }
            )
        return JsonResponse({"message": "error"}, status=400)


class NetworkCreator(View):
    """Django page for creating a network from a template."""

    def get(
        self,
        request: HttpRequest,
        *args,
        network_id: str = None,
        **kwargs,
    ):
        """Handle page get requests.

        Args:
            request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        network = NetworkManager.db.get(network_id)
        return render(
            request,
            "network_creator.html",
            {
                "sidebar": get_sidebar(),
                "form": NetworkTemplateForm(),
                # "random_elements_form": NetworkFormManager.get_or_create_form(network_id),
                "network_json": json.dumps(network.to_dict(json_serializable=True)),
                "network_name": network.doc_metadata.name,
                "network_id": network.doc_metadata.uuid,
            },
        )

    def post(
        self,
        request: HttpRequest,
        *args,
        network_id: str = None,
        **kwargs,
    ):
        """Handle page post requests.

        :param request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        creator_type = request.POST.get("type")
        if creator_type == "Mesh":
            network = network_creator.create_mesh(
                size=int(request.POST.get("size")),
                connectivity=float(request.POST.get("connectivity")),
            )
        elif creator_type == "Star":
            network = network_creator.create_star(
                first_layer_size=int(request.POST.get("first_layer_size")),
                group_size=int(request.POST.get("star_group_size")),
                group_connectivity=float(
                    request.POST.get("star_group_connectivity")
                ),
            )
        elif creator_type == "P2P":
            network = network_creator.create_p2p(
                inter_group_connectivity=float(
                    request.POST.get("inter_group_connectivity")
                ),
                group_size=int(request.POST.get("P2P_group_size")),
                group_connectivity=float(
                    request.POST.get("P2P_group_connectivity")
                ),
            )
        elif creator_type == "Ring":
            network = network_creator.create_ring(
                break_probability=float(request.POST.get("break_probability")),
                ring_size=int(request.POST.get("ring_size")),
            )
        current_network = NetworkManager.db.get(network_id)
        network._doc_metadata = (
            current_network.doc_metadata
        )  # copy the metadata from the old to the new network instance
        NetworkManager.db.update(network=network)
        network_form = NetworkFormManager.get_or_create_form(network_id)
        network_form.network = network
        return JsonResponse(
            {
                "network_json": json.dumps(network.to_dict(json_serializable=True)),
                "network_id": network.doc_metadata.uuid,
            }
        )


class NodeEditor(View):
    """
    Django representation of node_editor.html.

    implements 'get' and 'post' methods to handle page requests.
    """

    def get(self, request: HttpRequest, *args, network_id: str = None, **kwargs):
        """Handle page get requests.

        Args:
            request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        network_form = NetworkFormManager.get_or_create_form(network_id)
        return render(
            request,
            "node_editor.html",
            {
                "sidebar": get_sidebar(),
                "form": network_form,
                "protected": network_form.network.doc_metadata.locked,
                "toolbar": default_toolbar,
                "network_id": network_id,
                "network_json": json.dumps(
                    network_form.network.to_dict(json_serializable=True)
                ),
            },
        )

    def post(self, request: HttpRequest, *args, network_id: str = None, **kwargs):
        """Handle page post requests.

        :param request: A Django `request` object that contains the data passed from
            the html page. A `request` object will always be delivered when a page
            object is accessed.
        """
        body = request.body.decode("utf-8")
        io = StringIO(body)
        dict_n: dict = json.load(io)

        # find network id as not passed
        network_id = dict_n["_doc_metadata"]["uuid"]

        NetworkFormManager.update_network_elements(network_id, dict_n)
        return JsonResponse({"message": "success"})


class GameModeConfigView(View):
    """Django page template for game mode creation and editing."""

    def get(
        self,
        request: HttpRequest,
        *args,
        game_mode_id: str = None,
        section_name: str = None,
        **kwargs,
    ):
        """
        Handle page get requests.

        :param request: the Django page `request` object containing the html data for `game_mode_config.html` and the server GET / POST request bodies.
        :param game_mode_id: a game mode filename passed within the page url parameters
        :param section_name: the section of the config file the page was displaying; one of (red,blue,game_rules,observation_space,rewards,reset,miscellaneous)

        :return: Html string representing an instance of the`GameModeConfigView`
        """
        if game_mode_id is None:
            raise (
                Http404(
                    f"Can't find game mode section {section_name} in game mode {game_mode_id}"
                )
            )

        game_mode_form = GameModeFormManager.get_or_create_form(game_mode_id)
        section = game_mode_form.get_section(section_name)
        return self.render_page(request, section, game_mode_form)

    def post(
        self,
        request: HttpRequest,
        *args,
        game_mode_id: str = None,
        section_name: str = None,
        **kwargs,
    ):
        """
        Handle page post requests.

        :param request: the Django page `request` object containing the html data for `game_mode_config.html` and the server GET / POST request bodies.
        :param game_mode_id: a game mode filename passed within the page url parameters
        :param section_name: the section of the config file the page was displaying; one of (red,blue,game_rules,observation_space,rewards,reset,miscellaneous)

        :return: Html string representing an instance of the`GameModeConfigView`
        """
        game_mode_form = GameModeFormManager.get_or_create_form(game_mode_id)
        section = game_mode_form.get_section(section_name)
        if section.config_class.validation.passed:
            if (
                section_name == game_mode_form.last_section.name
                and game_mode_form.game_mode.validation.passed
            ):
                GameModeFormManager.save_as_game_mode(game_mode_form)
                return redirect("Manage game modes")
            return redirect(
                "game mode config",
                game_mode_id,
                game_mode_form.get_next_section_name(section_name),
            )
        return self.render_page(request, section, game_mode_form)

    def render_page(
        self,
        request: HttpRequest,
        section: GameModeSection,
        game_mode_form: GameModeForm,
    ):
        """
        Process pythonic tags in game_mode_config.html and return formatted page.

        :param request: the Django page `request` object containing the html data and the server GET / POST request bodies.
        :param game_mode_id: a game mode filename passed within the page url parameters
        :param section_name: the section of the config file the page was displaying; one of (red,blue,game_rules,observation_space,rewards,reset,miscellaneous)
        :param error_message: an optional error message string to be displayed in the `#error-message` html element

        :return: Html string representing an instance of the`GameModeConfigView`
        """
        return render(
            request,
            "game_mode_config.html",
            {
                "sections": game_mode_form.sections,
                "section": section,
                "doc_metadata_form": game_mode_form.doc_metadata_form,
                "current_section_name": section.name,
                "last": False,
                "sidebar": get_sidebar(),
                "game_mode_name": game_mode_form.game_mode.doc_metadata.name,
                "game_mode_id": game_mode_form.game_mode.doc_metadata.uuid,
                "game_mode_description": game_mode_form.game_mode.doc_metadata.description if game_mode_form.game_mode.doc_metadata.description else "",
                "protected": game_mode_form.game_mode.doc_metadata.locked,
            },
        )


def db_manager(request: HttpRequest) -> JsonResponse:
    """
    Create, edit, delete config yaml files.

    Extract `operation`,`game_mode_name` and optional `source_game_mode` from POST request body and
    use the information to perform the appropriate alteration to the
    game mode files contained in the `GAME_MODES_DIR`.

    :param request: here the django_request object will be specifically loaded with
        `operation`,`game_mode_name` and optional `source_game_mode` parameters.

    :return:
        `JsonResponse` object with either success code 500 (generic success) or
        error code 400 (generic error) containing a message.
    """
    if request.method == "POST":
        operation = request.POST.get("operation")
        item_type = request.POST.get("item_type")

        item_names = request.POST.getlist("item_names[]")
        item_ids = request.POST.getlist("item_ids[]")

        item_name = item_names[0] if item_names else None
        # item_id = item_ids[0] if item_ids else None

        def create_game_mode():
            game_mode = GameMode()
            GameModeManager.db.insert(game_mode=game_mode, name=item_name)
            return reverse(
                "game mode config",
                kwargs={"game_mode_id": game_mode.doc_metadata.uuid},
            )

        def create_network():
            network = NetworkManager.db.insert(network=Network(), name=item_name)
            return reverse(
                "node editor",
                kwargs={"network_id": network.doc_metadata.uuid},
            )

        def create_template_network():
            network = NetworkManager.db.insert(network=Network(), name=item_name)
            return reverse(
                "network creator",
                kwargs={"network_id": network.doc_metadata.uuid},
            )

        def delete_game_mode():
            for id in item_ids:
                GameModeManager.db.remove(GameModeManager.db.get(id))
            return "reload"

        def delete_network():
            for id in item_ids:
                NetworkManager.db.remove(NetworkManager.db.get(id))
            return "reload"

        def create_game_mode_from():
            game_mode = GameModeManager.db.get(request.POST.get("source_item_id"))            
            game_mode._doc_metadata = DocMetadata()
            GameModeManager.db.insert(game_mode=game_mode, name=item_name)
            return reverse(
                "game mode config",
                kwargs={"game_mode_id": game_mode.doc_metadata.uuid},
            )

        def create_network_from():
            network = NetworkManager.db.get(request.POST.get("source_item_id"))          
            network._doc_metadata = DocMetadata()
            NetworkManager.db.insert(network=network, name=item_name)
            return reverse(
                "node editor",
                kwargs={"network_id": network.doc_metadata.uuid},
            )

        operations = {
            "game mode": {
                "create": create_game_mode,
                "delete": delete_game_mode,
                "create from": create_game_mode_from,
            },
            "network": {
                "create": create_network,
                "delete": delete_network,
                "create from": create_network_from,
                "template": create_template_network,
            },
        }
        try:
            return JsonResponse({"load": operations[item_type][operation]()})
        except KeyError as e:
            return JsonResponse({"message:": str(e)}, status=400)
    return JsonResponse({"message:": "FAILED"}, status=400)


def update_game_mode(request: HttpRequest) -> JsonResponse:
    """
    Update the :attribute: `edited_forms` dictionary with the current state of the config and check for errors.

    Check the current contents of the :class:`ConfigForm <yawning_titan_gui.forms.ConfigForm>` are valid
    using the criteria defined in the appropriate section of the :class:`~yawning_titan.game_modes.game_mode.GameMode`

    :param request: here the django_request object will be specifically loaded with
        `section_name`,`game_mode_id`parameters as well as the form data.

    :return: response object containing error if config is invalid or redirect parameters if valid
    """
    if request.method == "POST":
        print("POSTED",request.POST)
        game_mode_id = request.POST.get("_game_mode_id")
        operation = request.POST.get("_operation")
        game_mode_form = GameModeFormManager.get_or_create_form(game_mode_id)
        if operation == "save":
            GameModeFormManager.save_as_game_mode(game_mode_form)
            return JsonResponse({"message": "saved"})
        elif operation == "update":
            section_name = request.POST.get("_section_name")      
            if section_name == "doc-meta":
                game_mode_form.update_doc_meta(data=request.POST)
            form_id = int(request.POST.get("_form_id"))      
            section = game_mode_form.update_section(
                section_name=section_name, form_id=form_id, data=request.POST
            )
            if section.config_class.validation.passed:
                return JsonResponse({"message": "updated"})
            else:
                return JsonResponse(
                    {"errors": json.dumps(section.get_form_errors())}, status=400
                )
    return JsonResponse({"message": "Invalid operation"})


def update_network(request: HttpRequest) -> JsonResponse:
    """
    Update the :class: `~yawning_titan_gui.forms.network_forms.NetworkForm` with the given `_network_id`.

    Use the data packaged within the POST request to update the value of :class: `~yawning_titan.networks.network.Network` associated
    with the network form.

    :param request: here the django_request object will be specifically loaded with
        `_network_id` parameter as well as the form data.

    :return: response object containing error if config is invalid or a json representation of a network if valid.
    """
    if request.method == "POST":
        network_form = NetworkFormManager.update_network_attributes(
            request.POST.get("_network_id"), request.POST
        )
        return JsonResponse(
            {
                "network_json": json.dumps(
                    network_form.network.to_dict(json_serializable=True)
                )
            }
        )
    return JsonResponse({"message": "Invalid operation"})
