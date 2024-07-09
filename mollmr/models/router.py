from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from openai import AsyncOpenAI

from mollmr.models.request import Request
from mollmr.models.mixture import Mixture
from mollmr.models.model import Model
from mollmr.config.config import config


@dataclass
class Router:
    model: Optional[Model] = None
    mixtures: defaultdict[str, list[Mixture]] = field(
        default_factory=lambda: defaultdict(list)
    )

    @staticmethod
    def load_from_config() -> Optional['Router']:
        mixture_list: list[Mixture] = Mixture.load_from_config()
        mixtures = {}
        for mixture in mixture_list:
            mixtures[mixture.name] = mixture
            for nested_model in [mixture.aggregate_model, *mixture.worker_models]:
                if nested_model.name not in mixtures:
                    mixtures[nested_model.name] = Mixture(
                        name=nested_model.name, aggregate_model=nested_model
                    )
        if len(mixtures) < 1:
            raise Exception('Could not find any mixtures in the config')
        router = Router()
        if not config.get('router', {}).get('model'):
            print(
                'Router not defined: if attempting to route calls, please ensure config is correct (see example). Defaulting to first mixture.'
            )
        else:
            try:
                router = Router(model=Model(**config['router']['model']))
            except Exception as e:
                print(f'Failed to create router from config: {e}')
        router.mixtures = mixtures
        return router

    async def get_mixture_for_request(self, request: Request):
        if len(self.mixtures) < 1:
            raise Exception(
                'No mixtures found - please configure mixtures in config.yaml'
            )
        if request.model == 'router' and not self.model:
            raise Exception('router selected, but config did not provide a model')
        if request.model != 'router':
            mixture = self.mixtures.get(request.model)
            if not mixture:
                raise Exception(f'Failed to find mixture for: {request.model}')
            return mixture

        mixture_list = self.mixtures.values()
        mixture_options = [mixture for mixture in mixture_list if mixture.description]
        if len(mixture_options) < 1:
            raise Exception('router selected, but missing mixture descriptions')

        mixture_options_string = ''
        for mixture_option in mixture_options:
            mixture_options_string += (
                f'{mixture_option.name}: {mixture_option.description}\n'
            )
        prompt = f'''
        QUESTION: {request.messages[-1].content}

        Given the question above, please select a mixture from below based on the description.
        This will be parsed as is, so please do not include any formatting, just the mixture name.

        MIXTURES:
        {mixture_options_string}
        '''
        response = await self.model.prompt(prompt)
        selection = response.choices[0].message.content.strip()
        for mixture in mixture_options:
            if mixture.name == selection:
                return mixture
        raise Exception(f'Failed to match mixture: {selection}')

    @staticmethod
    async def get_models_from_provider(base_url: str, api_key: str):
        client_list = await AsyncOpenAI(
            base_url=base_url, api_key=api_key
        ).models.list()
        return [
            Model(name=model_info.id, base_url=base_url, api_key=api_key)
            for model_info in client_list.data
        ]
