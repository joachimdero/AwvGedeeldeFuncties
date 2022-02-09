from OTLMOW.OTLModel.Classes.AfschermendeConstructie import AfschermendeConstructie
from OTLMOW.OTLModel.Classes.Geleideconstructie import Geleideconstructie
from OTLMOW.OTLModel.Classes.GetesteBeginconstructie import GetesteBeginconstructie

from UploadAfschermendeConstructies.EventDataAC import EventDataAC


class DataToAssetProcessor:
    def process_eventDataAC_to_assets(self, eventDataAC: EventDataAC) -> [AfschermendeConstructie]:
        if eventDataAC.typeAC == '' and eventDataAC.materiaal == '' and eventDataAC.product == '':  # en fabrikant!
            asset = Geleideconstructie()
            asset.geometry = eventDataAC.wktLineStringZM
            return [asset]
        if eventDataAC.typeAC == 'begin- en eindconstructie':
            if eventDataAC.product == 'Beginconstructie SafeEnd P4 - terminal':
                asset = GetesteBeginconstructie()
                asset.geometry = eventDataAC.wktLineStringZM
                asset.productnaam = 'SafeEnd P4 - terminal'
                asset.productidentificatiecode.producent = 'Saferoad Holland BV'
                asset.productidentificatiecode.linkTechnischeFiche = 'https://www.saferoad.nl/contentassets/eb7874415681447eb4f6a869011d5099/working-instruction---safeend-p4.pdf'
                return [asset]
        return []
      
