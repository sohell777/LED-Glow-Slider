import { buttonStatus } from './set_button_status';

export default function handler(req, res) {
    res.status(200).json(buttonStatus);
}
