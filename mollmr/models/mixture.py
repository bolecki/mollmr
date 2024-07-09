import asyncio

from dataclasses import dataclass, field
from typing import Optional

from mollmr.models.request import Request
from mollmr.models.model import Model
from mollmr.config.config import config


@dataclass
class Mixture:
    name: str
    aggregate_model: Model
    worker_models: list[Model] = field(default_factory=list)
    description: Optional[str] = None

    @staticmethod
    def load_from_config():
        mixtures = []
        for mixture_data in config['mixtures']:
            aggregate_model = Model(**mixture_data['aggregate'])
            worker_models = [
                Model(**worker) if isinstance(worker, dict) else Model(name=worker)
                for worker in mixture_data['workers']
            ]

            mixture = Mixture(
                name=mixture_data['name'],
                description=mixture_data.get('description', None),
                aggregate_model=aggregate_model,
                worker_models=worker_models,
            )
            mixtures.append(mixture)
        return mixtures

    @staticmethod
    def get_mixture(name: str):
        for mixture in Mixture.load_from_config():
            if mixture.name == name:
                return mixture
        return None

    @staticmethod
    async def _collect_response(request: Request, model: Model):
        print(f'loading response for: {model.name}')
        return await model.generate(request=request, stream=False)

    async def _collect_worker_responses(self, request: Request):
        tasks = []

        for model in self.worker_models:
            task = asyncio.create_task(
                self._collect_response(request=request, model=model)
            )
            tasks.append(task)

        worker_results = await asyncio.gather(*tasks)

        for model, response in zip(self.worker_models, worker_results):
            print(
                f'RESPONSE - {model.name}:\n{response.choices[0].message.content}\n\n\n\n'
            )

        return worker_results

    @staticmethod
    def _get_aggregate_prompt(request: Request, worker_results: dict):
        prompt = f'''
        Given the question: {request.messages[-1].content}
        And the following worker responses: {[result.choices[0].message.content for result in worker_results]}
        Please craft a final response by combining the best parts of the worker responses.

        Final Response:

        '''

        print('prompt for aggregate: ', prompt)

        return prompt

    async def _get_base_request(self, request: Request):
        if len(self.worker_models) == 0:
            return request
        worker_results = await self._collect_worker_responses(request)
        prompt = self._get_aggregate_prompt(
            request=request, worker_results=worker_results
        )
        request.messages[-1].content = prompt
        return request

    async def generate(self, request: Request):
        request = await self._get_base_request(request=request)
        return await self.aggregate_model.generate(
            request=request, stream=request.stream
        )
