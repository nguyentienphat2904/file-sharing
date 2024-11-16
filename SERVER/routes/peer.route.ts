import express, { Request, Response } from "express";
import { PeerController } from "../controller/peer.controller";

const router = express.Router();
const peerController = new PeerController();

router.get('/discover', peerController.discover);
router.get('/ping', peerController.ping);
router.post('/register', peerController.register)

export default router;