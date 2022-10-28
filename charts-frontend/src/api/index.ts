import ky from 'ky';
import { InterfaceResponse } from 'interfaces/index';

export const api = ky.extend({
  timeout: 3000,
  hooks: {
    beforeError: [
      async (error) => {
        const { response } = error;
        // Сформируем человекообразное сообщение об ошибке
        if (response && response.body) {
          const r: InterfaceResponse = JSON.parse(await response.text()) as InterfaceResponse;
          error.message = `(${response.status}) ${(r.errors || []).join()}`;
        }
        return error;
      },
    ],
  },
});
